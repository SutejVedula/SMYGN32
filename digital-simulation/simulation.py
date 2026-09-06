import pygame
import math

# ============================================================
# SMYGN32 - SMART MINE VEHICLE SAFETY SYSTEM
# DIGITAL SIMULATION - INTEGRATED DEMO MODE
#
# 4 vehicles are shown on the haul road.
# Stage 3 adds simulated Radar, LiDAR, GPS/DGPS and V2V quality.
# A/B = primary V2V collision-risk pair
# C/D = supporting fleet vehicles
#
# Controls:
# 1..5  = scenarios
# R     = reset scenario
# SPACE = pause/resume
# D     = automatic 5-scenario demo mode
# F11   = fullscreen
# ESC   = exit fullscreen
# ============================================================

pygame.init()

BASE_W, BASE_H = 1280, 720
WINDOW_W, WINDOW_H = 1280, 720
screen = pygame.display.set_mode((WINDOW_W, WINDOW_H), pygame.RESIZABLE)
pygame.display.set_caption("SMYGN32 - Smart Mine Vehicle Safety System")
canvas = pygame.Surface((BASE_W, BASE_H))
clock = pygame.time.Clock()

# ------------------------------------------------------------
# COLORS
# ------------------------------------------------------------
BG = (10, 13, 16)
PANEL = (27, 31, 36)
PANEL_ALT = (22, 27, 31)
PANEL_BORDER = (58, 64, 70)
WHITE = (242, 242, 242)
LIGHT = (190, 195, 200)
GRAY = (110, 115, 120)
DARK_GRAY = (70, 75, 80)
BLACK = (0, 0, 0)
ROAD = (64, 68, 73)
ROAD_LINE = (235, 235, 235)
BLUE = (40, 145, 235)
CYAN = (30, 190, 240)
GREEN = (35, 210, 100)
YELLOW = (255, 205, 35)
RED = (245, 60, 65)
ORANGE = (245, 145, 30)
PURPLE = (180, 90, 245)

# ------------------------------------------------------------
# FONTS
# ------------------------------------------------------------
def make_font(size, bold=False):
    return pygame.font.SysFont("Arial", size, bold=bold)

FONT_TITLE = make_font(32, True)
FONT_SUBTITLE = make_font(17, True)
FONT_STATUS = make_font(24, True)
FONT_SECTION = make_font(18, True)
FONT_NORMAL = make_font(15)
FONT_NORMAL_BOLD = make_font(15, True)
FONT_SMALL = make_font(12)
FONT_SMALL_BOLD = make_font(12, True)
FONT_TINY = make_font(10)
FONT_TINY_BOLD = make_font(10, True)

# ------------------------------------------------------------
# GLOBAL STATE
# ------------------------------------------------------------
scenario = 1
paused = False
simulation_time = 0.0

truck_a_speed = 15.0
truck_b_speed = 10.0
distance = 140.0
fog_visibility = 80.0
risk_score = 10
risk_level = "SAFE"
trajectory = "STABLE"
collision_avoided = False
collision_occurred = False

v2v_connected = True
radar_active = True
lidar_active = True
gps_locked = True
visibility_active = True

# ------------------------------------------------------------
# SENSOR FUSION STATE
# ------------------------------------------------------------
radar_distance = 140.0
lidar_distance = 140.0
v2v_distance = 140.0
radar_confidence = 96.0
lidar_confidence = 97.0
gps_confidence = 99.0
v2v_confidence = 99.0
v2v_latency = 35.0
fused_distance = 140.0
fusion_confidence = 97.0
sensor_state = "NORMAL"
safe_speed_recommendation = 25.0

# ------------------------------------------------------------
# TRAJECTORY PREDICTION STATE
# ------------------------------------------------------------
prediction_horizon = 5.0
predicted_a_position = 250.0
predicted_b_position = 760.0
predicted_conflict_x = None
predicted_conflict_time = None
prediction_confidence = 95.0
prediction_state = "STABLE"
prediction_distance = 140.0

truck_a_position = 260.0
truck_b_position = 760.0
truck_a_direction = 1
truck_b_direction = 1

# Supporting vehicles: visible in the simulation but not part of A/B TTC.
truck_c_position = 140.0
truck_d_position = 900.0
truck_c_speed = 18.0
truck_d_speed = 12.0

fullscreen = False

# ------------------------------------------------------------
# AUTOMATIC DEMO MODE
# ------------------------------------------------------------
demo_mode = False
demo_elapsed = 0.0
DEMO_DURATIONS = {
    1: 5.5,   # SAFE
    2: 5.5,   # CAUTION
    3: 6.0,   # CRITICAL + collision impact
    4: 6.0,   # COLLISION AVOIDED + safe-crossing hold
    5: 5.5,   # DENSE FOG
}

# ------------------------------------------------------------
# COMMAND CENTER / INCIDENT LOG
# ------------------------------------------------------------
event_log = []
last_logged_priority = ""
last_logged_action = ""

# ------------------------------------------------------------
# DYNAMIC VEHICLE / SAFETY RESPONSE STATE
# ------------------------------------------------------------
target_a_speed = 15.0
target_b_speed = 10.0
base_a_speed = 15.0
base_b_speed = 10.0
speed_control_mode = "NORMAL"
peak_risk = 10
risk_history = []
risk_history_times = []
last_risk_band = ""
collision_event_logged = False
avoidance_start_time = None

# Collision / avoidance visual demonstration state.
collision_effect_time = 0.0
collision_effect_duration = 2.2
collision_blast_center = None
avoidance_crossed = False

# Vehicle dynamics are intentionally conservative so the demo
# visibly shows speed reduction before the conflict point.
ACCEL_RATE_KMHPS = 4.0

def add_event(message, level="INFO"):
    """Add a compact timestamped event to the command-center log."""
    if len(event_log) >= 7:
        event_log.pop(0)
    event_log.append({
        "time": simulation_time,
        "message": message,
        "level": level
    })

# ------------------------------------------------------------
# FLEET DATA
# ------------------------------------------------------------
fleet = {
    "A01": {"speed": 15.0, "zone": "HR-01", "state": "ACTIVE", "color": BLUE},
    "B01": {"speed": 10.0, "zone": "HR-01", "state": "ACTIVE", "color": ORANGE},
    "C01": {"speed": 18.0, "zone": "HR-02", "state": "ACTIVE", "color": PURPLE},
    "D01": {"speed": 12.0, "zone": "HR-03", "state": "ACTIVE", "color": GREEN},
}

# ============================================================
# TEXT / PANEL HELPERS
# ============================================================
def draw_text(surface, text, x, y, font, color=WHITE):
    surface.blit(font.render(str(text), True, color), (int(x), int(y)))


def draw_text_fit(surface, text, x, y, font, color, max_width, align="left"):
    """Draw text inside a fixed-width field without overflow."""
    text = str(text)
    if font.size(text)[0] > max_width:
        clipped = text
        while clipped and font.size(clipped + "...")[0] > max_width:
            clipped = clipped[:-1]
        text = clipped + "..." if clipped else "..."
    img = font.render(text, True, color)
    if align == "right":
        draw_x = x + max_width - img.get_width()
    elif align == "center":
        draw_x = x + (max_width - img.get_width()) / 2
    else:
        draw_x = x
    surface.blit(img, (int(draw_x), int(y)))

def centered_text(surface, text, center_x, y, font, color=WHITE):
    img = font.render(str(text), True, color)
    surface.blit(img, (int(center_x - img.get_width() / 2), int(y)))


def fit_text(text, font, max_width):
    """Shorten text with ... so it can never overflow a card."""
    text = str(text)
    if font.size(text)[0] <= max_width:
        return text
    while text and font.size(text + "...")[0] > max_width:
        text = text[:-1]
    return text + "..."


def draw_panel(surface, rect, title):
    pygame.draw.rect(surface, PANEL, rect, border_radius=4)
    pygame.draw.rect(surface, PANEL_BORDER, rect, 1, border_radius=4)
    draw_text(surface, title, rect.x + 16, rect.y + 12, FONT_SECTION, WHITE)


def draw_metric(surface, label, value, x, y, value_color=WHITE, label_width=125):
    draw_text(surface, label, x, y, FONT_NORMAL, LIGHT)
    draw_text(surface, value, x + label_width, y, FONT_NORMAL_BOLD, value_color)

# ============================================================
# SCENARIOS
# ============================================================
def reset_supporting_vehicles():
    global truck_c_position, truck_d_position
    truck_c_position = 150.0
    truck_d_position = 900.0


def set_scenario(number):
    global scenario, simulation_time, collision_avoided, collision_occurred
    global truck_a_speed, truck_b_speed, distance, fog_visibility
    global risk_score, risk_level, trajectory
    global truck_a_position, truck_b_position, collision_occurred
    global collision_effect_time, collision_blast_center
    global collision_avoided, avoidance_crossed
    global truck_a_direction, truck_b_direction
    global last_logged_priority, last_logged_action
    global target_a_speed, target_b_speed, base_a_speed, base_b_speed
    global speed_control_mode, peak_risk
    global risk_history, risk_history_times, last_risk_band
    global collision_event_logged, avoidance_start_time
    global collision_effect_time, collision_blast_center, avoidance_crossed
    global demo_elapsed

    scenario = number
    simulation_time = 0.0
    demo_elapsed = 0.0
    collision_avoided = False
    collision_occurred = False
    reset_supporting_vehicles()

    risk_history = []
    risk_history_times = []
    peak_risk = 0
    last_risk_band = ""
    collision_event_logged = False
    avoidance_start_time = None
    collision_effect_time = 0.0
    collision_blast_center = None
    avoidance_crossed = False
    speed_control_mode = "NORMAL"

    if number == 1:
        base_a_speed, base_b_speed = 15.0, 10.0
        distance = 140.0
        fog_visibility = 80.0
        risk_score, risk_level, trajectory = 10, "SAFE", "STABLE"
        truck_a_position, truck_b_position = 250.0, 760.0
        truck_a_direction, truck_b_direction = 1, 1

    elif number == 2:
        base_a_speed, base_b_speed = 15.0, 10.0
        distance = 70.0
        fog_visibility = 50.0
        risk_score, risk_level, trajectory = 30, "CAUTION", "CONVERGING"
        truck_a_position, truck_b_position = 330.0, 830.0
        truck_a_direction, truck_b_direction = 1, -1

    elif number == 3:
        base_a_speed, base_b_speed = 35.0, 25.0
        distance = 58.7
        fog_visibility = 50.0
        risk_score, risk_level, trajectory = 88, "CRITICAL", "CONVERGING"
        truck_a_position, truck_b_position = 365.0, 815.0
        truck_a_direction, truck_b_direction = 1, -1

    elif number == 4:
        # Collision-avoided demonstration:
        # both vehicles approach, safely pass/cross each other, then HOLD
        # their positions. There is no automatic braking.
        base_a_speed, base_b_speed = 18.0, 14.0
        distance = 42.0
        fog_visibility = 30.0
        risk_score, risk_level, trajectory = 0, "COLLISION AVOIDED", "CONVERGING"
        collision_avoided = False
        truck_a_position, truck_b_position = 390.0, 700.0
        truck_a_direction, truck_b_direction = 1, -1

    elif number == 5:
        base_a_speed, base_b_speed = 15.0, 10.0
        distance = 70.0
        fog_visibility = 5.0
        risk_score, risk_level, trajectory = 70, "CAUTION", "CONVERGING"
        truck_a_position, truck_b_position = 330.0, 830.0
        truck_a_direction, truck_b_direction = 1, -1

    target_a_speed = base_a_speed
    target_b_speed = base_b_speed
    truck_a_speed = base_a_speed
    truck_b_speed = base_b_speed

    update_fleet_context()
    last_logged_priority = ""
    last_logged_action = ""
    add_event(f"SCENARIO {scenario} LOADED", "INFO")

# ============================================================
# SENSOR FUSION ENGINE - STAGE 4
# ============================================================
def clamp(value, low, high):
    return max(low, min(high, value))


def update_sensor_fusion():
    """
    Simulates independent sensor measurements and confidence.
    Radar remains relatively robust in fog, LiDAR degrades more,
    GPS degrades slightly, and V2V quality is primarily affected
    by link latency/quality rather than visibility.
    """
    global radar_distance, lidar_distance, v2v_distance
    global radar_confidence, lidar_confidence, gps_confidence
    global v2v_confidence, v2v_latency
    global fused_distance, fusion_confidence
    global sensor_state, safe_speed_recommendation

    true_distance = max(0.1, distance)

    # Visibility factor: 80m+ is effectively clear for this simulation.
    fog_factor = clamp(fog_visibility / 80.0, 0.05, 1.0)

    # Deterministic, slowly changing sensor noise for a stable demo.
    noise_wave = math.sin(simulation_time * 2.7)

    # Radar: robust in fog, with moderate measurement noise.
    radar_confidence = clamp(90.0 + fog_factor * 8.0 + noise_wave * 1.5, 70.0, 99.0)
    radar_error = (1.0 - radar_confidence / 100.0) * 3.5
    radar_distance = max(
        0.1,
        true_distance + math.sin(simulation_time * 3.1) * radar_error
    )

    # LiDAR: strongly affected by dense fog.
    lidar_confidence = clamp(38.0 + fog_factor * 60.0 + noise_wave * 2.0, 25.0, 98.0)
    lidar_error = (1.0 - lidar_confidence / 100.0) * 7.0
    lidar_distance = max(
        0.1,
        true_distance + math.sin(simulation_time * 4.4 + 0.8) * lidar_error
    )

    # GPS/DGPS: generally stable, with slight degradation in severe conditions.
    gps_confidence = clamp(93.0 + fog_factor * 6.0 + math.sin(simulation_time * 1.5) * 1.0, 88.0, 99.5)

    # V2V: communication quality remains high, but latency rises slightly
    # as conditions become difficult.
    v2v_confidence = clamp(96.0 + fog_factor * 3.0 + math.sin(simulation_time * 1.9) * 0.8, 90.0, 99.5)
    v2v_latency = clamp(28.0 + (1.0 - fog_factor) * 35.0 + abs(noise_wave) * 3.0, 25.0, 70.0)
    v2v_distance = max(
        0.1,
        true_distance + math.sin(simulation_time * 2.1 + 1.3) * (100.0 - v2v_confidence) * 0.04
    )

    # Weighted fusion. Higher-confidence measurements contribute more.
    measurements = [
        (radar_distance, radar_confidence),
        (lidar_distance, lidar_confidence),
        (v2v_distance, v2v_confidence),
    ]
    weight_sum = sum(conf for _, conf in measurements)

    if weight_sum > 0:
        fused_distance = sum(value * conf for value, conf in measurements) / weight_sum
    else:
        fused_distance = true_distance

    # Combined confidence with GPS as a supporting localization signal.
    fusion_confidence = (
        radar_confidence * 0.35
        + lidar_confidence * 0.25
        + v2v_confidence * 0.25
        + gps_confidence * 0.15
    )

    if fog_visibility <= 10:
        sensor_state = "DEGRADED / DENSE FOG"
    elif fog_visibility <= 30:
        sensor_state = "REDUCED VISIBILITY"
    else:
        sensor_state = "NORMAL"

    # Conservative speed recommendation for the operator.
    if risk_level == "CRITICAL":
        safe_speed_recommendation = 8.0
    elif risk_level == "CAUTION":
        safe_speed_recommendation = 12.0 if fog_visibility <= 10 else 18.0
    elif fog_visibility <= 10:
        safe_speed_recommendation = 12.0
    elif fog_visibility <= 30:
        safe_speed_recommendation = 18.0
    else:
        safe_speed_recommendation = 25.0


# ============================================================
# TRAJECTORY PREDICTION ENGINE - STAGE 4
# ============================================================
def update_trajectory_prediction():
    """
    Predicts where the primary A/B vehicles will be after a short
    horizon using current position, speed and direction.
    It also estimates whether their predicted paths converge.
    """
    global predicted_a_position, predicted_b_position
    global predicted_conflict_x, predicted_conflict_time
    global prediction_confidence, prediction_state, prediction_distance

    speed_scale = 2.0
    a_velocity = truck_a_speed * speed_scale * truck_a_direction
    b_velocity = truck_b_speed * speed_scale * truck_b_direction

    predicted_a_position = truck_a_position + a_velocity * prediction_horizon
    predicted_b_position = truck_b_position + b_velocity * prediction_horizon

    # Keep projected markers within the visible road coordinate range.
    predicted_a_position = clamp(predicted_a_position, 65.0, 1215.0)
    predicted_b_position = clamp(predicted_b_position, 65.0, 1215.0)

    # A simple crossing-time estimate for opposing traffic.
    predicted_conflict_x = None
    predicted_conflict_time = None

    if truck_a_direction != truck_b_direction and truck_a_speed + truck_b_speed > 0:
        # Positions are treated as the center reference of each truck.
        # Find the time when both linear paths meet.
        relative_velocity = a_velocity - b_velocity
        if abs(relative_velocity) > 0.001:
            meet_time = (truck_b_position - truck_a_position) / relative_velocity
            if 0.0 < meet_time <= 12.0:
                ax_at_meet = truck_a_position + a_velocity * meet_time
                bx_at_meet = truck_b_position + b_velocity * meet_time
                if abs(ax_at_meet - bx_at_meet) < 35:
                    predicted_conflict_x = int((ax_at_meet + bx_at_meet) / 2)
                    predicted_conflict_time = meet_time

    # Prediction confidence follows the quality of the fused sensor picture.
    prediction_confidence = clamp(
        fusion_confidence
        - max(0.0, (70.0 - lidar_confidence) * 0.12)
        - max(0.0, (80.0 - radar_confidence) * 0.06),
        55.0, 99.0
    )

    if scenario == 4:
        prediction_state = "STOPPED / SAFE"
    elif predicted_conflict_time is not None:
        if predicted_conflict_time <= 5.0:
            prediction_state = "HIGH CONVERGENCE"
        else:
            prediction_state = "CONVERGING"
    elif truck_a_direction == truck_b_direction:
        prediction_state = "STABLE"
    else:
        prediction_state = "DIVERGING"

    # Estimated predicted separation after the horizon.
    prediction_distance = abs(predicted_b_position - predicted_a_position)


def draw_prediction_overlay(surface, road_y):
    """
    Visualizes the 5-second predicted trajectory without adding
    clutter to the lower dashboard.
    """
    ax = position_to_screen(truck_a_position) + 36
    bx = position_to_screen(truck_b_position) + 36
    pax = position_to_screen(predicted_a_position) + 36
    pbx = position_to_screen(predicted_b_position) + 36

    path_y = road_y + 58

    # Thin projected paths.
    if scenario != 4:
        pygame.draw.line(surface, CYAN, (ax, path_y), (pax, path_y), 2)
        pygame.draw.line(surface, ORANGE, (bx, path_y), (pbx, path_y), 2)

        # 5-second endpoint markers.
        pygame.draw.circle(surface, CYAN, (int(pax), path_y), 5, 2)
        pygame.draw.circle(surface, ORANGE, (int(pbx), path_y), 5, 2)

        # Horizon label centered between predicted points.
        mid = (pax + pbx) / 2
        centered_text(surface, "5s PREDICTED PATH", mid, path_y - 18,
                      FONT_TINY_BOLD, LIGHT)

    if predicted_conflict_x is not None:
        conflict_y = road_y + 67
        pygame.draw.circle(surface, RED, (predicted_conflict_x, conflict_y), 9, 2)
        pygame.draw.circle(surface, YELLOW, (predicted_conflict_x, conflict_y), 4)
        centered_text(
            surface,
            f"CONFLICT ~{predicted_conflict_time:.1f}s",
            predicted_conflict_x,
            conflict_y + 17,
            FONT_TINY_BOLD,
            RED
        )

# ============================================================
# RISK ENGINE
# ============================================================
def relative_speed():
    if truck_a_direction != truck_b_direction:
        return truck_a_speed + truck_b_speed
    return abs(truck_a_speed - truck_b_speed)


def calculate_ttc():
    rel = relative_speed()
    if rel <= 0.01:
        return None
    measurement = fused_distance if fused_distance > 0 else distance
    return measurement / (rel * 1000.0 / 3600.0)


def update_risk():
    global risk_score, risk_level, trajectory

    if collision_avoided:
        risk_score = 0
        risk_level = "COLLISION AVOIDED"
        trajectory = "STOPPED"
        return

    ttc = calculate_ttc()
    if ttc is None:
        score = 5
    elif ttc < 4:
        score = 88
    elif ttc < 8:
        score = 75
    elif ttc < 15:
        score = 55
    elif ttc < 30:
        score = 30
    else:
        score = 10

    if fog_visibility <= 10:
        score += 15
    elif fog_visibility <= 30:
        score += 8

    # Low fused confidence adds a small uncertainty penalty.
    if fusion_confidence < 70:
        score += 8
    elif fusion_confidence < 82:
        score += 4

    if scenario == 1:
        score = 10
    elif scenario == 2:
        score = max(30, min(score, 70))
    elif scenario == 3:
        score = max(score, 88)
    elif scenario == 5:
        score = max(score, 55)

    risk_score = max(0, min(100, int(score)))

    if risk_score >= 75:
        risk_level = "CRITICAL"
    elif risk_score >= 25:
        risk_level = "CAUTION"
    else:
        risk_level = "SAFE"

    trajectory = "STABLE" if scenario == 1 else "CONVERGING"

# ============================================================
# INTELLIGENT DECISION ENGINE - STAGE 5
# ============================================================
def update_decision_engine():
    """Convert sensor/risk information into an operator warning.

    SMYGN32 does NOT automatically brake or control vehicle speed.
    Vehicles stop only in the simulation after a physical collision is
    detected, or in the predefined Scenario 4 collision-avoided demo.
    """
    global decision_action, decision_reason, decision_priority
    global brake_command, hazard_active, safe_speed_recommendation
    global last_logged_priority, last_logged_action

    ttc = calculate_ttc()
    hazard_active = False
    brake_command = "NONE"

    if collision_occurred:
        decision_priority = "COLLISION"
        decision_action = "COLLISION DETECTED — VEHICLES STOPPED"
        decision_reason = "PHYSICAL CONTACT / IMPACT EFFECT ACTIVE"
        hazard_active = True
    elif collision_avoided:
        decision_priority = "SAFE"
        decision_action = "COLLISION AVOIDED — HOLD POSITION"
        decision_reason = "SAFE GAP MAINTAINED / NO CONTACT"
    elif risk_score >= 88 or (ttc is not None and ttc <= 4.0):
        decision_priority = "EMERGENCY"
        decision_action = f"OPERATOR ALERT — STOP / SAFE SPEED ≤ {max(5, int(safe_speed_recommendation))} km/h"
        decision_reason = "CRITICAL TTC / CONVERGING TRAJECTORY"
        hazard_active = True
    elif risk_score >= 75 or (ttc is not None and ttc <= 8.0):
        decision_priority = "CRITICAL"
        decision_action = f"OPERATOR ALERT — REDUCE SPEED ≤ {max(8, int(safe_speed_recommendation))} km/h"
        decision_reason = "HIGH COLLISION RISK / LOW TTC"
        hazard_active = True
    elif risk_score >= 25 or (ttc is not None and ttc <= 15.0):
        decision_priority = "CAUTION"
        decision_action = f"OPERATOR ALERT — REDUCE SPEED ≤ {max(12, int(safe_speed_recommendation))} km/h"
        if prediction_state == "HIGH CONVERGENCE":
            decision_reason = "PREDICTED CONFLICT WITHIN 5 SEC"
        elif fog_visibility <= 10:
            decision_reason = "DENSE FOG / SENSOR UNCERTAINTY"
        else:
            decision_reason = "REDUCED SEPARATION / MONITOR VEHICLE"
        hazard_active = True
    elif fog_visibility <= 10:
        decision_priority = "CAUTION"
        decision_action = "OPERATOR ALERT — REDUCE SPEED ≤ 12 km/h"
        decision_reason = "DENSE FOG / MAINTAIN HIGH VISIBILITY MARGIN"
        hazard_active = True
    else:
        decision_priority = "NORMAL"
        decision_action = "MAINTAIN SPEED"
        decision_reason = "SAFE GAP / STABLE TRAJECTORY"

    if decision_priority != last_logged_priority or decision_action != last_logged_action:
        level = "ALERT" if decision_priority in ("COLLISION", "EMERGENCY", "CRITICAL") else "WARN" if decision_priority == "CAUTION" else "INFO"
        add_event(f"{decision_priority}: {decision_action}", level)
        last_logged_priority = decision_priority
        last_logged_action = decision_action

def decision_color():
    if decision_priority in ("COLLISION", "EMERGENCY"):
        return RED
    if decision_priority == "CRITICAL":
        return RED
    if decision_priority == "CAUTION":
        return YELLOW
    return GREEN


# ============================================================
# SIMULATION UPDATE
# ============================================================
def update_supporting_fleet(dt):
    global truck_c_position, truck_d_position
    truck_c_position += truck_c_speed * dt * 2.0
    truck_d_position -= truck_d_speed * dt * 2.0
    if truck_c_position > 960:
        truck_c_position = 120
    if truck_d_position < 100:
        truck_d_position = 920


def approach_speed(current, target, dt):
    """Smooth movement toward the driver's/current target speed."""
    if current < target:
        return min(target, current + ACCEL_RATE_KMHPS * dt)
    if current > target:
        return max(target, current - ACCEL_RATE_KMHPS * dt)
    return current


def update_dynamic_vehicle_control(dt):
    """Vehicle dynamics with operator-only safety recommendations.

    No automatic braking or automatic speed limiting is used. The only
    zero-speed state is the post-collision freeze for demonstration.
    """
    global truck_a_speed, truck_b_speed
    global target_a_speed, target_b_speed
    global speed_control_mode

    if scenario == 4:
        if avoidance_crossed:
            truck_a_speed = 0.0
            truck_b_speed = 0.0
            target_a_speed = target_b_speed = 0.0
            speed_control_mode = "COLLISION AVOIDED — HOLD"
        else:
            # Operator-controlled approach. SMYGN32 does not brake the vehicles.
            truck_a_speed = base_a_speed
            truck_b_speed = base_b_speed
            target_a_speed = base_a_speed
            target_b_speed = base_b_speed
            speed_control_mode = "OPERATOR CONTROL"
        return

    if collision_occurred:
        truck_a_speed = 0.0
        truck_b_speed = 0.0
        target_a_speed = target_b_speed = 0.0
        speed_control_mode = "POST-COLLISION STOP"
        return

    target_a_speed = base_a_speed
    target_b_speed = base_b_speed
    truck_a_speed = base_a_speed
    truck_b_speed = base_b_speed
    speed_control_mode = "OPERATOR CONTROL"

def record_risk_history():
    global peak_risk, last_risk_band
    peak_risk = max(peak_risk, risk_score)

    # Sample at ~5 Hz; keep a compact rolling history.
    if not risk_history_times or simulation_time - risk_history_times[-1] >= 0.20:
        risk_history.append(int(risk_score))
        risk_history_times.append(simulation_time)

        if len(risk_history) > 45:
            risk_history.pop(0)
            risk_history_times.pop(0)

    if risk_score >= 88:
        band = "CRITICAL"
    elif risk_score >= 75:
        band = "HIGH"
    elif risk_score >= 25:
        band = "CAUTION"
    else:
        band = "SAFE"

    if band != last_risk_band:
        if last_risk_band:
            level = "ALERT" if band in ("CRITICAL", "HIGH") else "WARN" if band == "CAUTION" else "INFO"
            add_event(f"RISK LEVEL → {band}", level)
        last_risk_band = band


def update_simulation(dt):
    # Explicitly declare every state variable written by this function.
    # This prevents the impact timer/state from being treated as local.
    global simulation_time, distance
    global truck_a_position, truck_b_position
    global truck_a_speed, truck_b_speed
    global target_a_speed, target_b_speed
    global speed_control_mode
    global collision_occurred, collision_avoided, avoidance_crossed
    global collision_effect_time, collision_blast_center
    global risk_score, risk_level, trajectory
    global collision_event_logged
    global demo_elapsed, demo_mode

    if paused:
        return

    # Keep the collision blast visible for a short time after impact.
    if collision_effect_time > 0.0:
        collision_effect_time = max(0.0, collision_effect_time - dt)

    simulation_time += dt
    if demo_mode:
        demo_elapsed += dt
    update_supporting_fleet(dt)

    # Vehicle movement uses the current dynamic speed.
    if scenario == 1:
        truck_a_position += truck_a_speed * dt * 2.0
        truck_b_position += truck_b_speed * dt * 2.0
        if truck_a_position > 850:
            truck_a_position = 250
        if truck_b_position > 900:
            truck_b_position = 550
        distance = 140.0

    elif scenario in (2, 3, 5):
        truck_a_position += truck_a_speed * dt * 2.0
        truck_b_position -= truck_b_speed * dt * 2.0

        if not collision_avoided:
            distance -= relative_speed() * 1000.0 / 3600.0 * dt

        # Scenarios 2 and 5 are repeating approach demonstrations.
        if scenario in (2, 5) and distance <= 30:
            truck_a_position, truck_b_position = 330.0, 830.0
            distance = 70.0
            add_event("SAFE RESET — APPROACH CYCLE RESTARTED", "INFO")

        # Scenario 3 reaches a real simulated contact point.
        # There is NO automatic braking: both vehicles keep their configured
        # speeds until contact, then the simulation freezes them.
        if scenario == 3 and not collision_occurred and distance <= 10.0:
            distance = 0.0
            collision_occurred = True
            truck_a_speed = 0.0
            truck_b_speed = 0.0
            target_a_speed = 0.0
            target_b_speed = 0.0
            speed_control_mode = "POST-COLLISION STOP"

            # Place both trucks at the contact point for a clear visual,
            # then trigger a non-gory impact/explosion effect.
            contact = (truck_a_position + truck_b_position) / 2.0
            truck_a_position = contact - 22.0
            truck_b_position = contact + 22.0
            collision_blast_center = contact
            collision_effect_time = collision_effect_duration
            add_event("COLLISION DETECTED — VEHICLES STOPPED", "ALERT")

    elif scenario == 4:
        if not avoidance_crossed:
            truck_a_position += truck_a_speed * dt * 2.0
            truck_b_position -= truck_b_speed * dt * 2.0

            # Let the two vehicles visibly pass one another.
            # Once their positions have crossed, freeze both at their
            # post-crossing positions to demonstrate a successful avoidance.
            if truck_a_position >= truck_b_position + 5.0:
                avoidance_crossed = True
                collision_avoided = True
                truck_a_speed = 0.0
                truck_b_speed = 0.0
                target_a_speed = target_b_speed = 0.0
                speed_control_mode = "COLLISION AVOIDED — HOLD"
                distance = 13.7
                risk_score = 0
                risk_level = "COLLISION AVOIDED"
                trajectory = "STOPPED"
                if not collision_event_logged:
                    add_event("COLLISION AVOIDED — VEHICLES CROSSED SAFELY", "INFO")
                    collision_event_logged = True
            else:
                distance = max(5.0, abs(truck_b_position - truck_a_position))
        else:
            # Hold the post-crossing positions indefinitely.
            truck_a_speed = 0.0
            truck_b_speed = 0.0
            distance = 13.7
            risk_score = 0
            risk_level = "COLLISION AVOIDED"
            trajectory = "STOPPED"

    if collision_occurred:
        truck_a_speed = 0.0
        truck_b_speed = 0.0
        target_a_speed = 0.0
        target_b_speed = 0.0
        speed_control_mode = "POST-COLLISION STOP"

    # First measure the world, then make a decision, then apply
    # the decision to vehicle speed.
    update_sensor_fusion()
    update_trajectory_prediction()
    update_risk()
    record_risk_history()
    update_decision_engine()
    update_dynamic_vehicle_control(dt)
    update_fleet_context()

    # Automatic SIH demonstration: progress through all five scenarios.
    # The demo never adds automatic braking; it only changes the displayed
    # scenario after its demonstration interval has completed.
    if demo_mode and demo_elapsed >= DEMO_DURATIONS.get(scenario, 5.5):
        next_scenario = scenario + 1 if scenario < 5 else 1
        add_event(
            f"DEMO: SCENARIO {scenario} COMPLETE — LOADING SCENARIO {next_scenario}",
            "INFO"
        )
        set_scenario(next_scenario)


# ============================================================
# FLEET STATE
# ============================================================
def update_fleet_context():
    fleet["A01"]["speed"] = truck_a_speed
    fleet["B01"]["speed"] = truck_b_speed
    fleet["C01"]["speed"] = truck_c_speed
    fleet["D01"]["speed"] = truck_d_speed

    if collision_avoided or collision_occurred:
        fleet["A01"]["state"] = "STOPPED"
        fleet["B01"]["state"] = "STOPPED"
    elif risk_level == "CRITICAL":
        fleet["A01"]["state"] = "ALERT"
        fleet["B01"]["state"] = "ALERT"
    elif risk_level == "CAUTION":
        fleet["A01"]["state"] = "CAUTION"
        fleet["B01"]["state"] = "CAUTION"
    else:
        fleet["A01"]["state"] = "ACTIVE"
        fleet["B01"]["state"] = "ACTIVE"

    fleet["C01"]["state"] = "ACTIVE"
    fleet["D01"]["state"] = "ACTIVE"

# ============================================================
# HEADER / STATUS
# ============================================================
def draw_header(surface):
    draw_text(surface, "SMYGN32", 40, 18, FONT_TITLE, WHITE)
    draw_text(surface, "V2V-Enabled Collision & Trajectory Risk Assessment  |  CENTRAL COMMAND", 40, 59,
              FONT_SUBTITLE, LIGHT)
    label = "SMART MINE VEHICLE SAFETY SYSTEM"
    img = FONT_NORMAL_BOLD.render(label, True, CYAN)
    surface.blit(img, (BASE_W - img.get_width() - 40, 28))


def draw_status_banner(surface):
    color = GREEN if risk_level in ("SAFE", "COLLISION AVOIDED") else YELLOW if risk_level == "CAUTION" else RED
    if risk_level == "SAFE":
        message = "SMYGN32 STATUS - SAFE"
    elif risk_level == "CAUTION":
        message = "SMYGN32 STATUS - CAUTION"
    elif risk_level == "CRITICAL":
        message = "SMYGN32 STATUS - CRITICAL"
    else:
        message = "SMYGN32 STATUS - COLLISION AVOIDED"

    rect = pygame.Rect(35, 102, BASE_W - 70, 52)
    pygame.draw.rect(surface, color, rect)
    pygame.draw.circle(surface, BLACK, (rect.x + 27, rect.centery), 7)
    centered_text(surface, message, BASE_W // 2 + 8, 113, FONT_STATUS, BLACK)

# ============================================================
# TOP ENVIRONMENT STRIP - NO OVERLAPPING ELEMENTS
# ============================================================
def draw_mine_environment(surface):
    rect = pygame.Rect(45, 166, BASE_W - 90, 50)
    pygame.draw.rect(surface, PANEL_ALT, rect, border_radius=4)
    pygame.draw.rect(surface, PANEL_BORDER, rect, 1, border_radius=4)

    cols = [
        (rect.x + 14, "MINE", "BAILADILA OPEN CAST", WHITE),
        (rect.x + 280, "ROAD", "WET / MONSOON", YELLOW),
        (rect.x + 500, "WIND", "18 km/h", LIGHT),
        (rect.x + 675, "RAIN", "12 mm/h", LIGHT),
        (rect.x + 850, "NETWORK", "ONLINE", GREEN),
    ]

    for x, label, value, color in cols:
        draw_text(surface, label, x, rect.y + 7, FONT_TINY_BOLD, GRAY)
        draw_text(surface, value, x, rect.y + 23, FONT_SMALL_BOLD, color)

# ============================================================
# ROAD + 4 VEHICLES
# ============================================================
def position_to_screen(position):
    road_x = 45
    road_w = BASE_W - 90
    usable = road_w - 170
    return road_x + 35 + int(max(0, min(1000, position)) / 1000.0 * usable)


def draw_truck(surface, x, y, truck_color, label, facing=1, small=False):
    x, y = int(x), int(y)
    if small:
        body_w, body_h = 58, 34
        cabin_w, cabin_h = 23, 22
        wheel_r = 8
        wheel_y = y + 36
        label_font = FONT_TINY_BOLD
        body = pygame.Rect(x, y, body_w, body_h)
        pygame.draw.rect(surface, truck_color, body, border_radius=2)
        cabin_x = x + 38 if facing == 1 else x - 5
        pygame.draw.rect(surface, truck_color, (cabin_x, y - 13, cabin_w, cabin_h), border_radius=2)
        if facing == 1:
            arrow = [(x + body_w, y + 10), (x + body_w + 14, y + 17), (x + body_w, y + 24)]
        else:
            arrow = [(x, y + 10), (x - 14, y + 17), (x, y + 24)]
        pygame.draw.polygon(surface, WHITE, arrow)
        for wx in (x + 16, x + 48):
            pygame.draw.circle(surface, BLACK, (wx, wheel_y), wheel_r)
            pygame.draw.circle(surface, GRAY, (wx, wheel_y), 3)
        centered_text(surface, label, x + body_w / 2, y + 43, label_font, WHITE)
        return

    body_w, body_h = 72, 50
    body = pygame.Rect(x, y, body_w, body_h)
    pygame.draw.rect(surface, truck_color, body, border_radius=2)
    cabin = pygame.Rect(x + 48, y - 20, 30, 30) if facing == 1 else pygame.Rect(x - 6, y - 20, 30, 30)
    pygame.draw.rect(surface, truck_color, cabin, border_radius=2)
    if facing == 1:
        arrow = [(x + 72, y + 15), (x + 92, y + 25), (x + 72, y + 35)]
    else:
        arrow = [(x, y + 15), (x - 20, y + 25), (x, y + 35)]
    pygame.draw.polygon(surface, WHITE, arrow)
    for wx in (x + 20, x + 62):
        pygame.draw.circle(surface, BLACK, (wx, y + 52), 11)
        pygame.draw.circle(surface, GRAY, (wx, y + 52), 4)
    centered_text(surface, label, x + 36, y + 66, FONT_SMALL_BOLD, WHITE)


def draw_v2v_link(surface, x1, x2, y):
    if not v2v_connected:
        return
    pygame.draw.line(surface, CYAN, (x1, y), (x2, y), 2)
    for i in range(5):
        progress = (simulation_time * 0.65 + i * 0.20) % 1.0
        x = x1 + (x2 - x1) * progress
        pygame.draw.circle(surface, CYAN, (int(x), y), 4)
    centered_text(surface, "V2V DATA EXCHANGE", (x1 + x2) / 2, y - 25, FONT_SMALL_BOLD, CYAN)


def draw_collision_effect(surface):
    """Animated non-gory vehicle-impact burst shown after Scenario 3 collision."""
    if collision_effect_time <= 0.0 or collision_blast_center is None:
        return

    x = position_to_screen(collision_blast_center)
    y = 229 + 74

    progress = 1.0 - (collision_effect_time / collision_effect_duration)
    progress = clamp(progress, 0.0, 1.0)

    # Expanding impact rings.
    radius = int(18 + progress * 42)
    pygame.draw.circle(surface, ORANGE, (x, y), radius, 3)
    pygame.draw.circle(surface, YELLOW, (x, y), max(8, radius // 2), 3)

    # Central flash.
    flash_r = int(max(5, 18 * (1.0 - progress)))
    pygame.draw.circle(surface, WHITE, (x, y), flash_r)

    # Animated debris / sparks.
    for i in range(12):
        angle = (i / 12.0) * math.tau + simulation_time * 2.2
        dist = 14 + progress * (28 + (i % 4) * 7)
        sx = int(x + math.cos(angle) * dist)
        sy = int(y + math.sin(angle) * dist * 0.65)
        size = 2 + (i % 2)
        pygame.draw.circle(surface, ORANGE if i % 2 else YELLOW, (sx, sy), size)

    # Smoke puffs rising above the impact point.
    for i in range(5):
        puff_progress = (progress * 1.15 + i * 0.13) % 1.0
        px = int(x - 18 + i * 9 + math.sin(simulation_time * 2 + i) * 5)
        py = int(y - 8 - puff_progress * 34)
        pr = int(5 + puff_progress * 7)
        pygame.draw.circle(surface, GRAY, (px, py), pr)

    centered_text(surface, "COLLISION IMPACT",
                   x, y + 43, FONT_TINY_BOLD, RED)


def draw_road(surface):
    road_x, road_y = 45, 229
    road_w, road_h = BASE_W - 90, 205
    pygame.draw.rect(surface, ROAD, (road_x, road_y, road_w, road_h))
    pygame.draw.line(surface, WHITE, (road_x, road_y), (road_x + road_w, road_y), 3)
    pygame.draw.line(surface, WHITE, (road_x, road_y + road_h), (road_x + road_w, road_y + road_h), 3)

    # Two clearly separated lanes.
    lane1_y = road_y + 67
    lane2_y = road_y + 143
    for x in range(road_x + 25, road_x + road_w - 25, 72):
        pygame.draw.rect(surface, ROAD_LINE, (x, lane1_y, 42, 5))
        pygame.draw.rect(surface, ROAD_LINE, (x, lane2_y, 42, 5))

    # Lane labels.
    draw_text(surface, "HAUL LANE 01", road_x + 15, road_y + 10, FONT_TINY_BOLD, LIGHT)
    draw_text(surface, "HAUL LANE 02", road_x + 15, road_y + 106, FONT_TINY_BOLD, LIGHT)

    # Primary A/B collision pair on lane 1.
    ax = position_to_screen(truck_a_position)
    bx = position_to_screen(truck_b_position)

    # After impact, visually throw the two trucks slightly apart while
    # their logical speeds remain 0 km/h. This is only a visual impact
    # effect; SMYGN32 does not automatically brake the vehicles.
    ax_draw, bx_draw = ax, bx
    if collision_occurred and collision_effect_time > 0.0:
        impact_progress = 1.0 - (collision_effect_time / collision_effect_duration)
        impact_progress = clamp(impact_progress, 0.0, 1.0)
        separation = int(impact_progress * 22)
        ax_draw -= separation
        bx_draw += separation

    draw_truck(surface, ax_draw, road_y + 48, BLUE, "TRUCK A", truck_a_direction)
    draw_truck(surface, bx_draw, road_y + 48, ORANGE, "TRUCK B", truck_b_direction)

    # Supporting C/D vehicles on lane 2.
    cx = position_to_screen(truck_c_position)
    dx = position_to_screen(truck_d_position)
    draw_truck(surface, cx, road_y + 132, PURPLE, "TRUCK C", 1, small=True)
    draw_truck(surface, dx, road_y + 132, GREEN, "TRUCK D", -1, small=True)

    # Impact animation appears above the stopped A/B vehicles.
    if collision_occurred:
        draw_collision_effect(surface)

    # Stage 4: predicted 5-second trajectories.
    draw_prediction_overlay(surface, road_y)

    # V2V line only between A/B, away from all environment text.
    if trajectory == "CONVERGING":
        left = min(ax + 70, bx + 70)
        right = max(ax, bx)
        if right - left > 70:
            draw_v2v_link(surface, left, right, road_y + 30)

        conflict_x = int((ax + bx + 45) / 2)
        conflict_y = road_y + 74
        pygame.draw.circle(surface, ORANGE, (conflict_x, conflict_y), 9)
        pygame.draw.circle(surface, WHITE, (conflict_x, conflict_y), 14, 2)
        centered_text(surface, "PREDICTED CONFLICT", conflict_x, road_y + 91, FONT_TINY_BOLD, ORANGE)
    else:
        draw_v2v_link(surface, min(ax, bx) + 30, max(ax, bx), road_y + 30)

# ============================================================
# ENVIRONMENT STATUS ROW
# ============================================================
def draw_environment_status(surface):
    # Fixed single-line telemetry bar. Every item owns a fixed x-range.
    y = 444
    items = [
        (45,  "FOG",     f"{fog_visibility:.0f}m",
         WHITE, 70),
        (135, "STATE",   "DENSE FOG" if fog_visibility <= 10 else "REDUCED" if fog_visibility <= 30 else "NORMAL",
         RED if fog_visibility <= 10 else YELLOW if fog_visibility <= 30 else GREEN, 125),
        (300, "FUSION",  f"{fusion_confidence:.0f}%",
         GREEN if fusion_confidence >= 80 else YELLOW, 95),
        (410, "PREDICT", f"{prediction_confidence:.0f}%",
         GREEN if prediction_confidence >= 80 else YELLOW, 95),
        (520, "V2V",     f"{v2v_latency:.0f}ms", CYAN, 95),
        (630, "GPS",     f"{gps_confidence:.0f}%", GREEN, 95),
        (740, "RADAR",   f"{radar_confidence:.0f}%",
         GREEN if radar_confidence >= 80 else YELLOW, 95),
        (850, "LiDAR",   f"{lidar_confidence:.0f}%",
         GREEN if lidar_confidence >= 70 else YELLOW if lidar_confidence >= 45 else RED, 95),
        (960, "ACTION",  decision_priority, decision_color(), 115),
    ]

    for x, label, value, color, width in items:
        draw_text(surface, label, x, y, FONT_TINY_BOLD, GRAY)
        draw_text_fit(surface, value, x + 48, y, FONT_TINY_BOLD, color, width - 48)

    speed_color = GREEN if safe_speed_recommendation >= 18 else YELLOW
    draw_text(surface, f"SAFE ≤ {safe_speed_recommendation:.0f} km/h",
              1090, y, FONT_TINY_BOLD, speed_color)

# ============================================================
# LOWER PANELS - 3 WIDE CARDS, NO CONGESTION
# ============================================================
def draw_sensor_panel(surface, rect):
    draw_panel(surface, rect, "SENSOR FUSION")

    rows = [
        ("RADAR", f"{radar_distance:.1f} m", radar_confidence),
        ("LiDAR", f"{lidar_distance:.1f} m", lidar_confidence),
        ("GPS / DGPS", "LOCKED", gps_confidence),
        ("V2V LINK", f"{v2v_latency:.0f} ms", v2v_confidence),
    ]

    y = rect.y + 39
    for name, value, conf in rows:
        draw_text_fit(surface, name, rect.x + 13, y, FONT_TINY_BOLD, LIGHT, 90)
        draw_text_fit(surface, value, rect.x + 105, y, FONT_TINY_BOLD, WHITE, 82)
        c = GREEN if conf >= 80 else YELLOW if conf >= 50 else RED
        img = FONT_TINY_BOLD.render(f"{conf:.0f}%", True, c)
        surface.blit(img, (rect.right - img.get_width() - 13, y))
        y += 20

    # Fusion result section.
    line_y = rect.y + 126
    pygame.draw.line(surface, PANEL_BORDER,
                     (rect.x + 13, line_y), (rect.right - 13, line_y), 1)

    draw_text(surface, "FUSED", rect.x + 13, line_y + 9,
              FONT_TINY_BOLD, GRAY)
    draw_text(surface, f"{fused_distance:.1f} m",
              rect.x + 105, line_y + 9, FONT_TINY_BOLD, CYAN)
    draw_text(surface, f"{fusion_confidence:.0f}%",
              rect.right - 53, line_y + 9, FONT_TINY_BOLD,
              GREEN if fusion_confidence >= 80 else YELLOW)

    state_color = RED if "DENSE" in sensor_state else YELLOW if "REDUCED" in sensor_state else GREEN
    draw_text_fit(surface, "SENSOR STATE", rect.x + 13, line_y + 31,
                  FONT_TINY, GRAY, 90)
    draw_text_fit(surface, sensor_state, rect.x + 105, line_y + 30,
                  FONT_TINY_BOLD, state_color, rect.w - 118)


def draw_risk_panel(surface, rect):
    draw_panel(surface, rect, "RISK & DECISION ENGINE")

    risk_color = GREEN if risk_level in ("SAFE", "COLLISION AVOIDED") else YELLOW if risk_level == "CAUTION" else RED
    pred_color = GREEN if prediction_state in ("STABLE", "STOPPED / SAFE") else YELLOW if prediction_state == "CONVERGING" else RED

    rows = [
        ("Fused Distance", f"{fused_distance:.1f} m", CYAN),
        ("TTC", "--" if calculate_ttc() is None else f"{calculate_ttc():.1f} s", WHITE),
        ("Risk Score", f"{risk_score}/100", risk_color),
        ("Risk Level", risk_level, risk_color),
        ("Prediction", prediction_state, pred_color),
    ]

    y = rect.y + 37
    for label, value, color in rows:
        draw_text_fit(surface, label, rect.x + 13, y, FONT_TINY_BOLD, LIGHT, 120)
        img = FONT_TINY_BOLD.render(value, True, color)
        surface.blit(img, (rect.right - img.get_width() - 13, y))
        y += 19

    # Decision strip is isolated below the metric rows.
    strip_y = rect.bottom - 48
    pygame.draw.rect(surface, PANEL_ALT,
                     (rect.x + 10, strip_y, rect.w - 20, 39),
                     border_radius=3)
    pygame.draw.rect(surface, decision_color(),
                     (rect.x + 10, strip_y, 4, 39),
                     border_radius=2)

    draw_text_fit(surface, decision_action,
                  rect.x + 21, strip_y + 5, FONT_TINY_BOLD,
                  decision_color(), rect.w - 42)

    draw_text_fit(surface, decision_reason,
                  rect.x + 21, strip_y + 23, FONT_TINY,
                  GRAY, rect.w - 42)


def draw_fleet_panel(surface, rect):
    draw_panel(surface, rect, "FLEET MONITOR")

    x_vehicle = rect.x + 13
    x_speed = rect.x + 103
    x_zone = rect.x + 195
    x_state = rect.x + 285

    for x, label in [(x_vehicle, "VEHICLE"), (x_speed, "SPEED"),
                     (x_zone, "ZONE"), (x_state, "STATE")]:
        draw_text(surface, label, x, rect.y + 36, FONT_TINY_BOLD, GRAY)

    y = rect.y + 55
    for vehicle_id, data in fleet.items():
        draw_text(surface, vehicle_id, x_vehicle, y,
                  FONT_TINY_BOLD, data["color"])
        draw_text(surface, f"{data['speed']:.0f}", x_speed, y,
                  FONT_TINY_BOLD, LIGHT)
        draw_text_fit(surface, data["zone"], x_zone, y,
                      FONT_TINY_BOLD, LIGHT, 65)

        state = data["state"]
        state_color = (
            RED if state == "ALERT" else
            YELLOW if state == "CAUTION" else
            GREEN
        )
        draw_text_fit(surface, state, x_state, y,
                      FONT_TINY_BOLD, state_color, rect.right - x_state - 13)
        y += 19

    # Fixed command area; fleet rows end above it.
    strip_y = rect.bottom - 47
    pygame.draw.rect(surface, PANEL_ALT,
                     (rect.x + 10, strip_y, rect.w - 20, 38),
                     border_radius=3)

    draw_text(surface, "OPERATOR COMMAND",
              rect.x + 18, strip_y + 4, FONT_TINY, GRAY)
    draw_text_fit(surface, "OPERATOR ACTION",
                  rect.x + 18, strip_y + 4, FONT_TINY, GRAY, rect.w - 36)
    draw_text_fit(surface, decision_action,
                  rect.x + 18, strip_y + 20, FONT_TINY_BOLD,
                  decision_color(), rect.w - 36)

# ============================================================
# CENTRAL MINE COMMAND CENTER
# ============================================================
def event_level_color(level):
    if level == "ALERT":
        return RED
    if level == "WARN":
        return YELLOW
    return CYAN




def draw_command_center_panel(surface, rect):
    """Fixed-grid command card. Every field has a reserved row and width."""
    draw_panel(surface, rect, "MINE COMMAND CENTER")

    pad = 10
    inner_x = rect.x + pad
    inner_w = rect.w - 2 * pad

    # Priority header
    y = rect.y + 31
    draw_text_fit(surface, "PRIORITY", inner_x, y, FONT_TINY_BOLD, GRAY, 55)
    draw_text_fit(surface, decision_priority, inner_x + 58, y,
                  FONT_TINY_BOLD, decision_color(), inner_w - 58, "right")

    # Main operator recommendation card — two dedicated lines.
    card_y = rect.y + 49
    card_h = 39
    card = pygame.Rect(inner_x, card_y, inner_w, card_h)
    pygame.draw.rect(surface, PANEL_ALT, card, border_radius=3)
    pygame.draw.rect(surface, decision_color(),
                     (card.x, card.y, 4, card.h), border_radius=2)
    draw_text_fit(surface, decision_action, card.x + 10, card.y + 5,
                  FONT_TINY_BOLD, decision_color(), card.w - 18)
    draw_text_fit(surface, decision_reason, card.x + 10, card.y + 23,
                  FONT_TINY, GRAY, card.w - 18)

    # Four metrics in a strict 2x2 grid.
    ttc = calculate_ttc()
    ttc_text = "--" if ttc is None else f"{ttc:.1f}s"
    metric_y = rect.y + 96
    col_w = inner_w // 2
    metric_rows = [
        (("TTC", ttc_text, CYAN), ("RISK", f"{risk_score}/100", RED if risk_score >= 75 else YELLOW if risk_score >= 25 else GREEN)),
        (("SAFE SPEED", f"≤ {safe_speed_recommendation:.0f} km/h", WHITE), ("SYSTEM", "ONLINE", GREEN)),
    ]
    for r, row in enumerate(metric_rows):
        yy = metric_y + r * 22
        for c, (label, value, color) in enumerate(row):
            xx = inner_x + c * col_w
            draw_text_fit(surface, label, xx, yy, FONT_TINY_BOLD, GRAY, 62)
            draw_text_fit(surface, value, xx + 64, yy, FONT_TINY_BOLD, color,
                          col_w - 66, "right")

    # Risk trend is a separate band, never sharing the metric rows.
    graph_y = rect.bottom - 36
    graph_x = inner_x + 72
    graph_w = inner_w - 72
    graph_h = 16
    draw_text_fit(surface, "RISK", inner_x, graph_y + 2, FONT_TINY_BOLD, GRAY, 62)
    pygame.draw.rect(surface, (25, 29, 33),
                     (graph_x, graph_y, graph_w, graph_h), border_radius=2)
    pygame.draw.rect(surface, PANEL_BORDER,
                     (graph_x, graph_y, graph_w, graph_h), 1, border_radius=2)
    if len(risk_history) >= 2:
        pts = []
        count = len(risk_history)
        for i, rv in enumerate(risk_history):
            px = graph_x + 2 + (graph_w - 4) * i / max(1, count - 1)
            py = graph_y + graph_h - 2 - (graph_h - 4) * clamp(rv, 0, 100) / 100.0
            pts.append((int(px), int(py)))
        pygame.draw.lines(surface,
                          RED if peak_risk >= 75 else YELLOW if peak_risk >= 25 else GREEN,
                          False, pts, 2)

    draw_text_fit(surface, "DECISION SUPPORT: ONLINE", inner_x, rect.bottom - 17,
                  FONT_TINY_BOLD, GREEN, inner_w, "center")

def draw_event_log_panel(surface, rect):
    """Event log with a hard row limit so entries never reach the footer."""
    draw_panel(surface, rect, "INCIDENT / EVENT LOG")

    draw_text_fit(surface, "TIME", rect.x + 8, rect.y + 31,
                  FONT_TINY_BOLD, GRAY, 42)
    draw_text_fit(surface, "EVENT", rect.x + 53, rect.y + 31,
                  FONT_TINY_BOLD, GRAY, rect.w - 61)

    footer_line_y = rect.bottom - 30
    row_h = 14
    first_y = rect.y + 48
    available = max(0, footer_line_y - first_y - 3)
    max_rows = max(1, int(available / row_h))

    visible_events = event_log[-max_rows:]
    y = first_y

    for item in reversed(visible_events):
        draw_text_fit(surface, f"{item['time']:04.1f}s",
                      rect.x + 8, y, FONT_TINY, GRAY, 42)
        draw_text_fit(surface, item["message"],
                      rect.x + 53, y, FONT_TINY_BOLD,
                      event_level_color(item["level"]), rect.w - 61)
        y += row_h

    pygame.draw.line(surface, PANEL_BORDER,
                     (rect.x + 8, footer_line_y),
                     (rect.right - 8, footer_line_y), 1)

    draw_text_fit(surface, "COMMAND CENTER • LIVE",
                  rect.x + 8, rect.bottom - 21,
                  FONT_TINY_BOLD, CYAN, rect.w - 16)


def draw_fleet_command_panel(surface, rect):
    """Fleet table whose summary occupies a dedicated bottom band."""
    draw_panel(surface, rect, "FLEET STATUS")

    # Column positions are calculated from panel width.
    id_x = rect.x + 8
    spd_x = rect.x + 43
    zone_x = rect.x + 78
    state_x = rect.x + 124

    draw_text_fit(surface, "ID", id_x, rect.y + 31,
                  FONT_TINY_BOLD, GRAY, 32)
    draw_text_fit(surface, "SPD", spd_x, rect.y + 31,
                  FONT_TINY_BOLD, GRAY, 32)
    draw_text_fit(surface, "ZONE", zone_x, rect.y + 31,
                  FONT_TINY_BOLD, GRAY, 44)
    draw_text_fit(surface, "STATE", state_x, rect.y + 31,
                  FONT_TINY_BOLD, GRAY, rect.right - state_x - 8)

    # Four vehicle rows in a fixed region.
    y = rect.y + 48
    for vehicle_id, data in list(fleet.items())[:4]:
        draw_text_fit(surface, vehicle_id, id_x, y,
                      FONT_TINY_BOLD, data["color"], 32)
        draw_text_fit(surface, f"{data['speed']:.0f}", spd_x, y,
                      FONT_TINY_BOLD, LIGHT, 32)
        draw_text_fit(surface, data["zone"], zone_x, y,
                      FONT_TINY_BOLD, LIGHT, 44)

        state = data["state"]
        state_color = RED if state == "ALERT" else YELLOW if state == "CAUTION" else GREEN
        draw_text_fit(surface, state, state_x, y,
                      FONT_TINY_BOLD, state_color, rect.right - state_x - 8)
        y += 15

    # Dedicated summary area; never shares rows with vehicle data.
    summary_y = rect.bottom - 43
    pygame.draw.line(surface, PANEL_BORDER,
                     (rect.x + 8, summary_y),
                     (rect.right - 8, summary_y), 1)

    active = sum(1 for d in fleet.values() if d["state"] == "ACTIVE")
    alerts = sum(1 for d in fleet.values()
                 if d["state"] in ("ALERT", "CAUTION"))

    draw_text_fit(surface, f"TRACKED {len(fleet)}",
                  rect.x + 8, summary_y + 6,
                  FONT_TINY_BOLD, CYAN, 70)
    draw_text_fit(surface, f"ACTIVE {active}",
                  rect.x + 82, summary_y + 6,
                  FONT_TINY_BOLD, GREEN, 62)
    draw_text_fit(surface, f"ALERTS {alerts}",
                  rect.x + 148, summary_y + 6,
                  FONT_TINY_BOLD, RED if alerts else GREEN,
                  rect.w - 156)

    draw_text_fit(surface,
                  f"V2V {v2v_confidence:.0f}%   GPS {gps_confidence:.0f}%",
                  rect.x + 8, rect.bottom - 21,
                  FONT_TINY_BOLD, CYAN, rect.w - 16, "center")


def draw_vehicle_oled_panel(surface, rect):
    """
    Vehicle-side OLED safety display.

    Every field has a fixed row. Text is clipped to its field, so
    changing values can never push another parameter outside the OLED.
    """
    draw_panel(surface, rect, "VEHICLE OLED • SAFETY DISPLAY")

    inner_x = rect.x + 9
    inner_y = rect.y + 33
    col_gap = 8
    col_w = (rect.w - 18 - col_gap * 2) // 3
    h = rect.h - 42

    sensor_rect = pygame.Rect(inner_x, inner_y, col_w, h)
    risk_rect = pygame.Rect(inner_x + col_w + col_gap, inner_y, col_w, h)
    pred_rect = pygame.Rect(inner_x + (col_w + col_gap) * 2,
                            inner_y, col_w, h)

    for r in (sensor_rect, risk_rect, pred_rect):
        pygame.draw.rect(surface, PANEL_ALT, r, border_radius=3)
        pygame.draw.rect(surface, PANEL_BORDER, r, 1, border_radius=3)

    # ---------------- SENSOR PARAMETERS ----------------
    draw_text_fit(surface, "SENSOR PARAMETERS",
                  sensor_rect.x + 6, sensor_rect.y + 5,
                  FONT_TINY_BOLD, CYAN, sensor_rect.w - 12)

    sensor_rows = [
        ("RADAR", f"{radar_distance:.1f}m", radar_confidence),
        ("LiDAR", f"{lidar_distance:.1f}m", lidar_confidence),
        ("V2V", f"{v2v_distance:.1f}m", v2v_confidence),
        ("GPS", f"{gps_confidence:.0f}%", gps_confidence),
        ("FUSION", f"{fused_distance:.1f}m", fusion_confidence),
    ]

    yy = sensor_rect.y + 25
    for label, value, conf in sensor_rows:
        draw_text_fit(surface, label, sensor_rect.x + 6, yy,
                      FONT_TINY_BOLD, GRAY, 47)
        draw_text_fit(surface, value, sensor_rect.x + 53, yy,
                      FONT_TINY_BOLD, WHITE, sensor_rect.w - 59, "right")
        yy += 14

    draw_text_fit(surface, f"CONF {fusion_confidence:.0f}%",
                  sensor_rect.x + 6, sensor_rect.bottom - 17,
                  FONT_TINY_BOLD,
                  GREEN if fusion_confidence >= 80 else YELLOW,
                  sensor_rect.w - 12, "center")

    # ---------------- RISK ASSESSMENT ----------------
    draw_text_fit(surface, "RISK ASSESSMENT",
                  risk_rect.x + 6, risk_rect.y + 5,
                  FONT_TINY_BOLD, YELLOW, risk_rect.w - 12)

    ttc = calculate_ttc()
    ttc_text = "--" if ttc is None else f"{ttc:.1f}s"
    risk_color = RED if risk_level == "CRITICAL" else YELLOW if risk_level == "CAUTION" else GREEN

    risk_rows = [
        ("DIST", f"{fused_distance:.1f}m"),
        ("REL SPD", f"{relative_speed():.1f}"),
        ("TTC", ttc_text),
        ("RISK", f"{risk_score}/100"),
        ("LEVEL", risk_level),
    ]

    yy = risk_rect.y + 25
    for label, value in risk_rows:
        draw_text_fit(surface, label, risk_rect.x + 6, yy,
                      FONT_TINY_BOLD, GRAY, 50)
        c = risk_color if label in ("RISK", "LEVEL") else WHITE
        draw_text_fit(surface, value, risk_rect.x + 56, yy,
                      FONT_TINY_BOLD, c, risk_rect.w - 62, "right")
        yy += 14

    # ---------------- PREDICTION ----------------
    draw_text_fit(surface, "PREDICTION",
                  pred_rect.x + 6, pred_rect.y + 5,
                  FONT_TINY_BOLD, ORANGE, pred_rect.w - 12)

    conflict = "--" if predicted_conflict_time is None else f"{predicted_conflict_time:.1f}s"
    prediction_rows = [
        ("HORIZON", f"{prediction_horizon:.0f}s"),
        ("STATE", prediction_state),
        ("CONF", f"{prediction_confidence:.0f}%"),
        ("CONFLICT", conflict),
    ]

    yy = pred_rect.y + 25
    for label, value in prediction_rows:
        draw_text_fit(surface, label, pred_rect.x + 6, yy,
                      FONT_TINY_BOLD, GRAY, 57)
        c = ORANGE if label == "STATE" and prediction_state == "CONVERGING" else WHITE
        draw_text_fit(surface, value, pred_rect.x + 63, yy,
                      FONT_TINY_BOLD, c, pred_rect.w - 69, "right")
        yy += 14

    # Dedicated action band.
    action_y = pred_rect.bottom - 35
    pygame.draw.line(surface, PANEL_BORDER,
                     (pred_rect.x + 6, action_y - 4),
                     (pred_rect.right - 6, action_y - 4), 1)

    draw_text_fit(surface, "ACTION",
                  pred_rect.x + 6, action_y,
                  FONT_TINY_BOLD, GRAY, 43)
    draw_text_fit(surface, decision_action,
                  pred_rect.x + 49, action_y,
                  FONT_TINY_BOLD, decision_color(),
                  pred_rect.w - 55, "right")

    draw_text_fit(surface,
                  f"SAFE <= {safe_speed_recommendation:.0f} km/h",
                  pred_rect.x + 6, pred_rect.bottom - 18,
                  FONT_TINY_BOLD,
                  GREEN if safe_speed_recommendation >= 18 else
                  YELLOW if safe_speed_recommendation >= 10 else RED,
                  pred_rect.w - 12, "center")

def draw_footer(surface):
    y = BASE_H - 22
    draw_text_fit(surface,
                  "1 SAFE   2 CAUTION   3 CRITICAL   4 COLLISION AVOIDED   5 DENSE FOG",
                  40, y, FONT_TINY_BOLD, LIGHT, 690)
    demo_label = "D DEMO ON" if demo_mode else "D DEMO"
    right_text = f"R RESET   SPACE PAUSE   {demo_label}   F11 FULLSCREEN   DEMO BUILD"
    draw_text_fit(surface, right_text,
                  BASE_W - 500, y, FONT_TINY_BOLD,
                  CYAN if demo_mode else LIGHT, 460, "right")

def toggle_demo_mode():
    global demo_mode, demo_elapsed
    demo_mode = not demo_mode
    demo_elapsed = 0.0
    if demo_mode:
        add_event("AUTOMATIC DEMO MODE STARTED", "INFO")
    else:
        add_event("AUTOMATIC DEMO MODE STOPPED", "INFO")


def toggle_fullscreen():
    global fullscreen, screen
    fullscreen = not fullscreen
    if fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((WINDOW_W, WINDOW_H), pygame.RESIZABLE)


def present():
    actual_w, actual_h = screen.get_size()
    scale = min(actual_w / BASE_W, actual_h / BASE_H)
    scaled_w = max(1, int(BASE_W * scale))
    scaled_h = max(1, int(BASE_H * scale))
    scaled = pygame.transform.smoothscale(canvas, (scaled_w, scaled_h))
    screen.fill(BG)
    screen.blit(scaled, ((actual_w - scaled_w) // 2, (actual_h - scaled_h) // 2))
    pygame.display.flip()

# ============================================================
# MAIN LOOP
# ============================================================
set_scenario(1)
add_event("SMYGN32 COMMAND CENTER ONLINE", "INFO")
add_event("PRESS D TO START AUTOMATIC 5-SCENARIO DEMO", "INFO")
update_sensor_fusion()
update_trajectory_prediction()
update_risk()
update_decision_engine()
running = True

while running:
    dt = min(clock.tick(60) / 1000.0, 0.05)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.VIDEORESIZE and not fullscreen:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if fullscreen:
                    toggle_fullscreen()
                else:
                    running = False
            elif event.key == pygame.K_1:
                if demo_mode:
                    demo_mode = False
                    add_event("AUTOMATIC DEMO MODE STOPPED — MANUAL CONTROL", "INFO")
                set_scenario(1)
            elif event.key == pygame.K_2:
                if demo_mode:
                    demo_mode = False
                    add_event("AUTOMATIC DEMO MODE STOPPED — MANUAL CONTROL", "INFO")
                set_scenario(2)
            elif event.key == pygame.K_3:
                if demo_mode:
                    demo_mode = False
                    add_event("AUTOMATIC DEMO MODE STOPPED — MANUAL CONTROL", "INFO")
                set_scenario(3)
            elif event.key == pygame.K_4:
                if demo_mode:
                    demo_mode = False
                    add_event("AUTOMATIC DEMO MODE STOPPED — MANUAL CONTROL", "INFO")
                set_scenario(4)
            elif event.key == pygame.K_5:
                if demo_mode:
                    demo_mode = False
                    add_event("AUTOMATIC DEMO MODE STOPPED — MANUAL CONTROL", "INFO")
                set_scenario(5)
            elif event.key == pygame.K_r:
                set_scenario(scenario)
            elif event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_d:
                toggle_demo_mode()
            elif event.key == pygame.K_F11:
                toggle_fullscreen()

    update_simulation(dt)

    canvas.fill(BG)
    draw_header(canvas)
    draw_status_banner(canvas)
    draw_mine_environment(canvas)
    draw_road(canvas)
    draw_environment_status(canvas)

    # ========================================================
    # FINAL FIXED TWO-ZONE DASHBOARD
    #
    # LEFT  = complete Central Mine Command Center
    # RIGHT = complete Vehicle OLED Safety Display
    #
    # Everything uses fixed coordinates and reserved bands.
    # No panel depends on the amount of text in another panel.
    # ========================================================
    lower_y = 455
    lower_h = 205
    outer_x = 45
    outer_w = BASE_W - 90
    split_gap = 16

    # 700 px command-center zone + remaining OLED zone.
    left_w = 700
    right_w = outer_w - left_w - split_gap

    # ---------------- LEFT: CENTRAL COMMAND CENTER ----------------
    left_rect = pygame.Rect(outer_x, lower_y, left_w, lower_h)
    pygame.draw.rect(canvas, (18, 22, 26), left_rect, border_radius=5)
    pygame.draw.rect(canvas, PANEL_BORDER, left_rect, 1, border_radius=5)

    draw_text_fit(canvas, "CENTRAL MINE COMMAND CENTER",
                  left_rect.x + 13, left_rect.y + 7,
                  FONT_SECTION, WHITE, left_rect.w - 26)

    sub_y = left_rect.y + 34
    sub_h = left_rect.h - 42
    sub_gap = 10

    # Wider command/log columns so their information remains readable.
    fleet_w = 185
    command_w = 245
    log_w = left_rect.w - 16 - fleet_w - command_w - (sub_gap * 2)

    fleet_rect = pygame.Rect(left_rect.x + 8, sub_y, fleet_w, sub_h)
    command_rect = pygame.Rect(fleet_rect.right + sub_gap, sub_y,
                               command_w, sub_h)
    log_rect = pygame.Rect(command_rect.right + sub_gap, sub_y,
                           log_w, sub_h)

    draw_fleet_command_panel(canvas, fleet_rect)
    draw_command_center_panel(canvas, command_rect)
    draw_event_log_panel(canvas, log_rect)

    # ---------------- RIGHT: VEHICLE OLED ----------------
    right_rect = pygame.Rect(left_rect.right + split_gap, lower_y,
                             right_w, lower_h)
    pygame.draw.rect(canvas, (18, 22, 26), right_rect, border_radius=5)
    pygame.draw.rect(canvas, CYAN, right_rect, 1, border_radius=5)

    draw_vehicle_oled_panel(canvas, right_rect)

    # Dedicated status strip below the dashboard.
    mode_text = "AUTOMATIC DEMO MODE" if demo_mode else "MANUAL CONTROL"
    centered_text(canvas,
                  f"SCENARIO {scenario}/5  |  DYNAMIC SAFETY + COMMAND CENTER + VEHICLE OLED  |  {mode_text}",
                  BASE_W // 2, 673, FONT_TINY_BOLD, CYAN if demo_mode else LIGHT)
    if demo_mode and not paused:
        remaining = max(0.0, DEMO_DURATIONS.get(scenario, 5.5) - demo_elapsed)
        centered_text(canvas, f"NEXT SCENARIO IN {remaining:.1f}s",
                      BASE_W // 2, 647, FONT_SMALL_BOLD, CYAN)
    elif paused:
        centered_text(canvas, "SIMULATION PAUSED",
                      BASE_W // 2, 647, FONT_SMALL_BOLD, YELLOW)
    draw_footer(canvas)
    present()

pygame.quit()
