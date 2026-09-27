import sys 
import os
import math
import random
import ctypes

from PySide6.QtCore import (
    QUrl,
    Qt,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
    QRectF,
    QPointF,
)
from PySide6.QtGui import (
    QPainter,
    QColor,
    QPen,
    QBrush,
    QFont,
    QPixmap,
    QLinearGradient,
    QIcon,
    QKeyEvent,
    QPainterPath,
)
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
    QGraphicsOpacityEffect,
)


# --- Windows Taskbar AppUserModelID Fix ---
if sys.platform == "win32":
    my_app_id = "fraunhofer.cobot.hmi.controller.1.0"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)


# --- Custom Clickable Progress/Parameter Slider ---
class ClickableSlider(QSlider):

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:

            if self.orientation() == Qt.Orientation.Horizontal:
                val = (
                    self.minimum()
                    + (self.maximum() - self.minimum())
                    * event.position().x()
                    / self.width()
                )
            else:
                val = (
                    self.minimum()
                    + (self.maximum() - self.minimum())
                    * (self.height() - event.position().y())
                    / self.height()
                )

            self.setValue(int(val))
            self.sliderMoved.emit(int(val))
            event.accept()

        super().mousePressEvent(event)


# --- Realistic Futuristic 6-DOF Cobot Visualizer ---
class CyberCobotVisualizer(QWidget):
    """Compact futuristic industrial cobot visualizer with harmonious kinematically coupled movements."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumSize(620, 230)
        self.setMaximumHeight(250)

        self.phase = 0.0

        # Multi-target configurations
        self.targets = [
            {"rel_x": 0.76, "rel_y": 0.48, "offset": 0.0},
            {"rel_x": 0.86, "rel_y": 0.28, "offset": 1.5},
            {"rel_x": 0.72, "rel_y": 0.76, "offset": 3.1},
        ]

        self.particles = []
        for _ in range(35):
            self.particles.append(
                {
                    "x": random.uniform(0, 1),
                    "y": random.uniform(0, 1),
                    "speed": random.uniform(0.0008, 0.002),
                    "size": random.uniform(1.0, 2.8),
                    "alpha": random.randint(45, 150),
                }
            )

        # Matrix Rain Background Text
        self.matrix_cols = 28
        self.matrix_chars = ["0", "1", "A", "F", "X", "9", "3", "7", "C", "E", "4", "B"]
        self.matrix_streams = []
        for i in range(self.matrix_cols):
            self.matrix_streams.append(
                {
                    "x_pct": (i + 0.5) / self.matrix_cols,
                    "y_pct": random.uniform(0, 1),
                    "speed": random.uniform(0.003, 0.008),
                    "chars": [random.choice(self.matrix_chars) for _ in range(6)],
                }
            )

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)

    def animate(self):
        self.phase += 0.025  # Smooth clock for fluid motion

        for particle in self.particles:
            particle["y"] -= particle["speed"]
            if particle["y"] < 0:
                particle["y"] = 1.0
                particle["x"] = random.uniform(0, 1)

        for stream in self.matrix_streams:
            stream["y_pct"] += stream["speed"]
            if stream["y_pct"] > 1.2:
                stream["y_pct"] = -0.2
                stream["chars"] = [random.choice(self.matrix_chars) for _ in range(6)]

        self.update()

    def _draw_arrow(self, painter, start_pt, end_pt, is_primary=False):
        """Helper to draw a directional vector arrow using QPainterPath."""
        dx = end_pt.x() - start_pt.x()
        dy = end_pt.y() - start_pt.y()
        angle = math.atan2(dy, dx)
        dist = math.hypot(dx, dy)

        if dist < 10:
            return

        arrow_size = 8 if is_primary else 6
        head_x = end_pt.x() - (arrow_size + 4) * math.cos(angle)
        head_y = end_pt.y() - (arrow_size + 4) * math.sin(angle)

        pen_color = QColor(0, 220, 170, 160) if is_primary else QColor(0, 150, 255, 80)
        pen_style = Qt.PenStyle.DashLine if not is_primary else Qt.PenStyle.SolidLine
        painter.setPen(QPen(pen_color, 1.2, pen_style))
        painter.drawLine(start_pt, QPointF(head_x, head_y))

        p1 = QPointF(
            head_x + arrow_size * math.cos(angle),
            head_y + arrow_size * math.sin(angle),
        )
        p2 = QPointF(
            head_x + arrow_size * 0.5 * math.cos(angle + math.pi * 0.75),
            head_y + arrow_size * 0.5 * math.sin(angle + math.pi * 0.75),
        )
        p3 = QPointF(
            head_x + arrow_size * 0.5 * math.cos(angle - math.pi * 0.75),
            head_y + arrow_size * 0.5 * math.sin(angle - math.pi * 0.75),
        )

        arrow_path = QPainterPath()
        arrow_path.moveTo(p1)
        arrow_path.lineTo(p2)
        arrow_path.lineTo(p3)
        arrow_path.closeSubpath()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(pen_color))
        painter.drawPath(arrow_path)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        width = self.width()
        height = self.height()

        if width <= 0 or height <= 0:
            return

        # Background Gradient
        background_gradient = QLinearGradient(0, 0, width, height)
        background_gradient.setColorAt(0.0, QColor(2, 8, 18))
        background_gradient.setColorAt(0.55, QColor(4, 17, 29))
        background_gradient.setColorAt(1.0, QColor(2, 10, 20))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(background_gradient))
        painter.drawRoundedRect(QRectF(0, 0, width, height), 8, 8)

        # Matrix Rain Background
        font = QFont("Consolas", 8, QFont.Weight.Bold)
        painter.setFont(font)

        for stream in self.matrix_streams:
            sx = stream["x_pct"] * width
            sy = stream["y_pct"] * height

            for idx, ch in enumerate(stream["chars"]):
                char_y = sy - (idx * 13)
                if 0 <= char_y <= height:
                    alpha = max(10, int(130 - idx * 22))
                    painter.setPen(QPen(QColor(0, 180, 120, alpha)))
                    painter.drawText(QPointF(sx, char_y), ch)

        # Technical Grid
        grid_spacing = max(20, int(width / 32))
        painter.setPen(QPen(QColor(20, 90, 125, 35), 1))

        for x in range(0, width + grid_spacing, grid_spacing):
            painter.drawLine(x, 0, x, height)

        for y in range(0, height + grid_spacing, grid_spacing):
            painter.drawLine(0, y, width, y)

        # Floating Particles
        painter.setPen(Qt.PenStyle.NoPen)
        for particle in self.particles:
            particle_x = particle["x"] * width
            particle_y = particle["y"] * height
            pulse = 0.65 + 0.35 * math.sin(self.phase * 2.0 + particle["x"] * 8.0)
            alpha = int(particle["alpha"] * pulse)

            painter.setBrush(QBrush(QColor(0, 170, 120, alpha)))
            painter.drawEllipse(
                QPointF(particle_x, particle_y), particle["size"], particle["size"]
            )

        # Safe Drawing Bounds
        safe_left = width * 0.07
        safe_right = width * 0.93
        safe_top = height * 0.08
        safe_bottom = height * 0.91

        drawing_width = safe_right - safe_left
        drawing_height = safe_bottom - safe_top

        # Scanning Laser
        scan_x = width * 0.50 + width * 0.40 * math.sin(self.phase * 0.75)
        laser_gradient = QLinearGradient(scan_x - width * 0.07, 0, scan_x, 0)
        laser_gradient.setColorAt(0.0, QColor(0, 90, 255, 0))
        laser_gradient.setColorAt(0.75, QColor(0, 100, 255, 25))
        laser_gradient.setColorAt(1.0, QColor(0, 220, 170, 90))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(laser_gradient))
        painter.drawRect(
            QRectF(scan_x - width * 0.07, safe_top, width * 0.07, drawing_height)
        )

        painter.setPen(QPen(QColor(0, 190, 255, 170), 1.2))
        painter.drawLine(QPointF(scan_x, safe_top), QPointF(scan_x, safe_bottom))

        # Scale & Base Coordinates
        scale = min(drawing_width / 470.0, drawing_height / 205.0)
        base_x = width * 0.34
        base_y = height * 0.82

        # Harmonious Coupled Kinematic Motion
        sweep = math.sin(self.phase * 0.8)

        # Joint 1: Base elevation
        q1 = math.radians(-75.0 + 12.0 * sweep)

        # Joint 2: Elbow flexing in harmonic phase delay
        q2_rel = math.radians(72.0 + 16.0 * math.sin(self.phase * 0.8 - 0.7))
        q2 = q1 + q2_rel

        # Joint 3: Wrist orientation compensation
        q3_rel = math.radians(-50.0 + 14.0 * math.cos(self.phase * 0.8))
        q3 = q2 + q3_rel

        link_1 = 84 * scale
        link_2 = 70 * scale
        link_3 = 42 * scale

        shoulder_x = base_x + link_1 * math.cos(q1)
        shoulder_y = base_y + link_1 * math.sin(q1)

        elbow_x = shoulder_x + link_2 * math.cos(q2)
        elbow_y = shoulder_y + link_2 * math.sin(q2)

        wrist_x = elbow_x + link_3 * math.cos(q3)
        wrist_y = elbow_y + link_3 * math.sin(q3)

        flange_length = 17 * scale
        flange_x = wrist_x + flange_length * math.cos(q3)
        flange_y = wrist_y + flange_length * math.sin(q3)

        # Base Assembly
        base_width = 70 * scale
        base_height = 20 * scale
        base_rect = QRectF(
            base_x - base_width / 2, base_y - base_height / 2, base_width, base_height
        )

        base_gradient = QLinearGradient(
            base_rect.left(), base_rect.top(), base_rect.left(), base_rect.bottom()
        )
        base_gradient.setColorAt(0.0, QColor(90, 105, 115))
        base_gradient.setColorAt(0.45, QColor(40, 52, 62))
        base_gradient.setColorAt(1.0, QColor(12, 20, 27))

        painter.setPen(QPen(QColor(120, 220, 190, 190), 1.2))
        painter.setBrush(QBrush(base_gradient))
        painter.drawRoundedRect(base_rect, 5 * scale, 5 * scale)

        ring_radius_x = 24 * scale
        ring_radius_y = 6 * scale

        painter.setPen(QPen(QColor(150, 175, 185, 180), 1.4))
        painter.setBrush(QBrush(QColor(15, 24, 31)))
        painter.drawEllipse(
            QPointF(base_x, base_y - 9 * scale), ring_radius_x, ring_radius_y
        )

        painter.setPen(QPen(QColor(0, 220, 155, 170), 1.2))
        painter.drawArc(
            QRectF(
                base_x - ring_radius_x,
                base_y - 9 * scale - ring_radius_y,
                ring_radius_x * 2,
                ring_radius_y * 2,
            ),
            15 * 16,
            150 * 16,
        )

        # Robot Link Drawing Helper
        def draw_robot_link(start_x, start_y, end_x, end_y, width_value):
            start_point = QPointF(start_x, start_y)
            end_point = QPointF(end_x, end_y)

            painter.setPen(
                QPen(
                    QColor(18, 28, 36),
                    width_value + 7 * scale,
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                )
            )
            painter.drawLine(start_point, end_point)

            painter.setPen(
                QPen(
                    QColor(88, 102, 111),
                    width_value,
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                )
            )
            painter.drawLine(start_point, end_point)

            painter.setPen(
                QPen(
                    QColor(0, 190, 135, 190),
                    max(1.2, width_value * 0.12),
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                )
            )
            painter.drawLine(
                QPointF(start_x, start_y - 1.2 * scale),
                QPointF(end_x, end_y - 1.2 * scale),
            )

        draw_robot_link(base_x, base_y - 9 * scale, shoulder_x, shoulder_y, 25 * scale)
        draw_robot_link(shoulder_x, shoulder_y, elbow_x, elbow_y, 21 * scale)
        draw_robot_link(elbow_x, elbow_y, wrist_x, wrist_y, 15 * scale)

        # Joint Housings
        def draw_joint(joint_x, joint_y, radius):
            outer_radius = radius * 1.35
            painter.setPen(QPen(QColor(8, 15, 21), 2 * scale))
            painter.setBrush(QBrush(QColor(54, 67, 76)))
            painter.drawEllipse(QPointF(joint_x, joint_y), outer_radius, outer_radius)

            painter.setPen(QPen(QColor(135, 150, 158), 1.2 * scale))
            painter.setBrush(QBrush(QColor(25, 35, 43)))
            painter.drawEllipse(QPointF(joint_x, joint_y), radius, radius)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(0, 220, 155)))
            painter.drawEllipse(
                QPointF(joint_x, joint_y), radius * 0.23, radius * 0.23
            )

        draw_joint(base_x, base_y - 9 * scale, 12 * scale)
        draw_joint(shoulder_x, shoulder_y, 13 * scale)
        draw_joint(elbow_x, elbow_y, 11 * scale)
        draw_joint(wrist_x, wrist_y, 8 * scale)

        # Wrist Flange & Gripper
        painter.save()
        painter.translate(flange_x, flange_y)
        painter.rotate(math.degrees(q3))

        flange_width = 25 * scale
        flange_height = 13 * scale

        painter.setPen(QPen(QColor(140, 155, 165), 1.2 * scale))
        painter.setBrush(QBrush(QColor(48, 61, 70)))
        painter.drawRoundedRect(
            QRectF(0, -flange_height / 2, flange_width, flange_height),
            3 * scale,
            3 * scale,
        )
        painter.restore()

        gripper_angle = q3 + math.pi / 2
        jaw_open = (7 + 2.5 * math.sin(self.phase * 1.6)) * scale
        jaw_length = 18 * scale

        jaw_1_start_x = flange_x + jaw_open * math.cos(gripper_angle)
        jaw_1_start_y = flange_y + jaw_open * math.sin(gripper_angle)
        jaw_2_start_x = flange_x - jaw_open * math.cos(gripper_angle)
        jaw_2_start_y = flange_y - jaw_open * math.sin(gripper_angle)

        jaw_1_end_x = jaw_1_start_x + jaw_length * math.cos(q3)
        jaw_1_end_y = jaw_1_start_y + jaw_length * math.sin(q3)
        jaw_2_end_x = jaw_2_start_x + jaw_length * math.cos(q3)
        jaw_2_end_y = jaw_2_start_y + jaw_length * math.sin(q3)

        painter.setPen(
            QPen(
                QColor(34, 46, 54),
                7 * scale,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )
        painter.drawLine(
            QPointF(jaw_1_start_x, jaw_1_start_y), QPointF(jaw_1_end_x, jaw_1_end_y)
        )
        painter.drawLine(
            QPointF(jaw_2_start_x, jaw_2_start_y), QPointF(jaw_2_end_x, jaw_2_end_y)
        )

        painter.setPen(
            QPen(
                QColor(145, 165, 175),
                3.5 * scale,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )
        painter.drawLine(
            QPointF(jaw_1_start_x, jaw_1_start_y), QPointF(jaw_1_end_x, jaw_1_end_y)
        )
        painter.drawLine(
            QPointF(jaw_2_start_x, jaw_2_start_y), QPointF(jaw_2_end_x, jaw_2_end_y)
        )

        painter.setPen(
            QPen(
                QColor(0, 220, 155),
                2 * scale,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )
        painter.drawLine(
            QPointF(jaw_1_end_x, jaw_1_end_y),
            QPointF(
                jaw_1_end_x + 5 * scale * math.cos(gripper_angle),
                jaw_1_end_y + 5 * scale * math.sin(gripper_angle),
            ),
        )
        painter.drawLine(
            QPointF(jaw_2_end_x, jaw_2_end_y),
            QPointF(
                jaw_2_end_x - 5 * scale * math.cos(gripper_angle),
                jaw_2_end_y - 5 * scale * math.sin(gripper_angle),
            ),
        )

        end_effector_pt = QPointF(
            (jaw_1_end_x + jaw_2_end_x) / 2.0, (jaw_1_end_y + jaw_2_end_y) / 2.0
        )

        # Multi-Target Reticles & Trajectory Vectors
        for idx, target in enumerate(self.targets):
            tx = width * target["rel_x"] + 8 * math.sin(
                self.phase * 0.9 + target["offset"]
            )
            ty = height * target["rel_y"] + 6 * math.cos(
                self.phase * 0.7 + target["offset"]
            )
            target_pt = QPointF(tx, ty)

            is_primary = idx == 0

            self._draw_arrow(painter, end_effector_pt, target_pt, is_primary=is_primary)

            t_radius = (
                min(22 * scale, height * 0.12)
                if is_primary
                else min(14 * scale, height * 0.08)
            )
            pulse = 1.0 + 0.12 * math.sin(self.phase * 2.0 + target["offset"])
            t_radius *= pulse

            ring_pen = (
                QPen(QColor(0, 220, 170, 200), 1.2)
                if is_primary
                else QPen(QColor(0, 140, 220, 120), 1.0, Qt.PenStyle.DashLine)
            )
            painter.setPen(ring_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(target_pt, t_radius, t_radius)

            if is_primary:
                painter.setPen(QPen(QColor(0, 220, 170, 180), 1))
                painter.drawEllipse(
                    target_pt, t_radius * 0.45, t_radius * 0.45
                )

            ch_len = t_radius * 1.3
            painter.setPen(
                QPen(
                    QColor(0, 220, 170, 160)
                    if is_primary
                    else QColor(0, 140, 220, 90),
                    1,
                )
            )
            painter.drawLine(QPointF(tx - ch_len, ty), QPointF(tx + ch_len, ty))
            painter.drawLine(QPointF(tx, ty - ch_len), QPointF(tx, ty + ch_len))

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(
                QBrush(
                    QColor(0, 220, 170, 220)
                    if is_primary
                    else QColor(0, 160, 240, 140)
                )
            )
            painter.drawEllipse(target_pt, 2.0, 2.0)

            font_lbl = QFont("Consolas", 6 if not is_primary else 7, QFont.Weight.Bold)
            painter.setFont(font_lbl)
            painter.setPen(
                QPen(
                    QColor(0, 220, 170, 180)
                    if is_primary
                    else QColor(0, 140, 220, 120)
                )
            )
            painter.drawText(
                QPointF(tx + t_radius + 3, ty - 2), f"TGT-0{idx+1}"
            )

        # Subtle Corner Brackets
        bracket_size = min(width * 0.035, 16)
        painter.setPen(QPen(QColor(0, 125, 255, 90), 1.2))

        painter.drawLine(safe_left, safe_top, safe_left + bracket_size, safe_top)
        painter.drawLine(safe_left, safe_top, safe_left, safe_top + bracket_size)

        painter.drawLine(safe_right, safe_top, safe_right - bracket_size, safe_top)
        painter.drawLine(safe_right, safe_top, safe_right, safe_top + bracket_size)

        painter.drawLine(safe_left, safe_bottom, safe_left + bracket_size, safe_bottom)
        painter.drawLine(safe_left, safe_bottom, safe_left, safe_bottom - bracket_size)

        painter.drawLine(
            safe_right, safe_bottom, safe_right - bracket_size, safe_bottom
        )
        painter.drawLine(
            safe_right, safe_bottom, safe_right, safe_bottom - bracket_size
        )


# --- Cyberpunk Fraunhofer Logo Reticle Widget ---
class CyberLogoHeader(QWidget):
    """Fraunhofer logo framed with deep blue HUD reticle corners."""

    def __init__(self, logo_path, parent=None):
        super().__init__(parent)

        self.setFixedHeight(75)
        self.logo_path = logo_path
        self.phase = 0.0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_hud)
        self.timer.start(30)

        # Inner Logo
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)

        self.logo_label = QLabel(self)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if os.path.exists(self.logo_path):
            pixmap = QPixmap(self.logo_path)
            scaled = pixmap.scaledToWidth(
                230, Qt.TransformationMode.SmoothTransformation
            )
            self.logo_label.setPixmap(scaled)
        else:
            self.logo_label.setText("Fraunhofer")
            self.logo_label.setFont(QFont("Arial", 22, QFont.Weight.Bold))
            self.logo_label.setStyleSheet("color: #008b52;")

        layout.addWidget(self.logo_label)

    def update_hud(self):
        self.phase += 0.08
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        c_len = 12
        pen = QPen(
            QColor(0, 51, 153, int(180 + 75 * math.sin(self.phase))),
            2,
        )
        painter.setPen(pen)

        # Top-Left Corner
        painter.drawLine(5, 5, 5 + c_len, 5)
        painter.drawLine(5, 5, 5, 5 + c_len)

        # Top-Right Corner
        painter.drawLine(width - 5, 5, width - 5 - c_len, 5)
        painter.drawLine(width - 5, 5, width - 5, 5 + c_len)

        # Bottom-Left Corner
        painter.drawLine(5, height - 5, 5 + c_len, height - 5)
        painter.drawLine(5, height - 5, 5, height - 5 - c_len)

        # Bottom-Right Corner
        painter.drawLine(width - 5, height - 5, width - 5 - c_len, height - 5)
        painter.drawLine(width - 5, height - 5, width - 5, height - 5 - c_len)


# --- Futuristic Cyber Intro Screen ---
class CyberCobotSplashScreen(QWidget):
    """Futuristic Cyber-Industrial Fraunhofer Intro Splash with Audio Soundtrack."""

    def __init__(self, on_finish_callback):
        super().__init__()

        self.on_finish_callback = on_finish_callback
        self.is_finished = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(760, 500)

        # Absolute paths for window icon
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        hmi_logo_jpg = os.path.join(BASE_DIR, "HMI_Logo.jpg")
        hmi_logo_png = os.path.join(BASE_DIR, "HMI_Logo.png")

        if os.path.exists(hmi_logo_jpg):
            self.setWindowIcon(QIcon(hmi_logo_jpg))
        elif os.path.exists(hmi_logo_png):
            self.setWindowIcon(QIcon(hmi_logo_png))

        # Setup Soundtrack Player
        self.intro_player = QMediaPlayer(self)
        self.intro_audio_output = QAudioOutput(self)
        self.intro_player.setAudioOutput(self.intro_audio_output)
        self.intro_audio_output.setVolume(0.7)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)

        container = QWidget(self)
        container.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0,
                    y1:0,
                    x2:1,
                    y2:1,
                    stop:0 #030812,
                    stop:0.55 #061321,
                    stop:1 #081628
                );
                border: 2px solid #0055ff;
                border-radius: 16px;
            }
        """)

        inner_layout = QVBoxLayout(container)
        inner_layout.setContentsMargins(22, 14, 22, 14)
        inner_layout.setSpacing(0)

        # Update the logo header instantiation with the absolute path
        fraunhofer_logo_path = os.path.join(BASE_DIR, "fraunhofer_logo.png")
        self.logo_header = CyberLogoHeader(fraunhofer_logo_path, self)
        
        sub_title = QLabel("AI-POWERED COBOT HMI", self)
        sub_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        sub_title.setStyleSheet("color: #ffffff; letter-spacing: 2px; border: none;")

        self.visualizer = CyberCobotVisualizer(self)

        self.status_text = QLabel("Preparing Environment...", self)
        self.status_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_text.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        self.status_text.setStyleSheet("color: #ffffff; border: none;")

        inner_layout.addWidget(self.logo_header)
        inner_layout.addSpacing(3)
        inner_layout.addWidget(sub_title)
        inner_layout.addSpacing(6)
        inner_layout.addWidget(self.visualizer, 1)
        inner_layout.addSpacing(6)
        inner_layout.addWidget(self.status_text)

        layout.addWidget(container)

        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

        QTimer.singleShot(
            1000,
            lambda: self.status_text.setText("Loading Features..."),
        )
        QTimer.singleShot(
            2000,
            lambda: self.status_text.setText("AI COBOT HMI Ready !")
        )

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_anim.setDuration(450)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Start visual animation and trigger soundtrack start
        self.fade_anim.start()
        self.play_soundtrack()

        QTimer.singleShot(3200, self.finish_intro)

    def play_soundtrack(self):
        """Play intro.mp3 using an absolute path."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        sound_path = os.path.join(base_dir, "intro.mp3")
        if os.path.exists(sound_path):
            try:
                self.intro_player.setSource(QUrl.fromLocalFile(sound_path))
                self.intro_player.play()
            except Exception as e:
                print(f"Audio playback skipped: {e}")

    def stop_soundtrack(self):
        """Stop audio playback cleanly when transitioning."""
        if self.intro_player:
            self.intro_player.stop()

    def finish_intro(self):
        """Clean up splash screen and invoke the main window callback."""
        if self.is_finished:
            return
        self.is_finished = True

        self.stop_soundtrack()
        self.close()

        if self.on_finish_callback:
            self.on_finish_callback()


# --- Main Industrial Cobot Controller HMI ---
class CobotControlHMI(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI COBOT HMI")
        self.resize(540, 400)

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        hmi_logo_jpg = os.path.join(BASE_DIR, "HMI_Logo.jpg")
        hmi_logo_png = os.path.join(BASE_DIR, "HMI_Logo.png")

        if os.path.exists(hmi_logo_jpg):
            self.setWindowIcon(QIcon(hmi_logo_jpg))
        elif os.path.exists(hmi_logo_png):
            self.setWindowIcon(QIcon(hmi_logo_png))

        self.setStyleSheet("""
            QWidget {
                background-color: #071322;
                color: #ffffff;
                font-family: Arial, sans-serif;
            }

            QLabel {
                font-size: 13px;
            }

            QPushButton {
                color: white;
                border: none;
                padding: 8px 14px;
                border-radius: 5px;
                font-weight: bold;
            }

            QSlider::groove:horizontal {
                border: 1px solid #1e3a5f;
                height: 8px;
                background: #102a45;
                border-radius: 4px;
            }

            QSlider::sub-page:horizontal {
                background: #008b52;
                border-radius: 4px;
            }

            QSlider::handle:horizontal {
                background: #ffffff;
                border: none;
                width: 16px;
                margin-top: -4px;
                margin-bottom: -4px;
                border-radius: 8px;
            }

            QSlider::handle:horizontal:hover {
                background: #006e40;
            }
        """)

        # Audio Components
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.5)

        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)

        layout = QVBoxLayout()
        layout.setSpacing(12)

        self.upload_btn = QPushButton("Load MP3 File", self)
        self.upload_btn.setStyleSheet("""
            QPushButton { background-color: #008b52; }
            QPushButton:hover { background-color: #006e40; }
            QPushButton:pressed { background-color: #005230; }
        """)
        self.upload_btn.clicked.connect(self.upload_file)
        layout.addWidget(self.upload_btn)

        self.status_label = QLabel("Status: Please Load a MP3 File", self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        button_layout = QHBoxLayout()

        self.rewind_btn = QPushButton("<< -5s", self)
        self.rewind_btn.setStyleSheet("""
            QPushButton { background-color: #37474f; }
            QPushButton:hover { background-color: #455a64; }
            QPushButton:pressed { background-color: #263238; }
        """)
        self.rewind_btn.clicked.connect(lambda: self.seek_relative(-5000))

        self.toggle_btn = QPushButton("Play", self)
        self.toggle_btn.setStyleSheet("""
            QPushButton { background-color: #003399; }
            QPushButton:hover { background-color: #002266; }
            QPushButton:pressed { background-color: #001133; }
        """)
        self.toggle_btn.clicked.connect(self.toggle_playback)

        self.restart_btn = QPushButton("Restart", self)
        self.restart_btn.setStyleSheet("""
            QPushButton { background-color: #e53935; }
            QPushButton:hover { background-color: #c62828; }
            QPushButton:pressed { background-color: #b71c1c; }
        """)
        self.restart_btn.clicked.connect(self.restart_music)

        self.forward_btn = QPushButton("+5s >>", self)
        self.forward_btn.setStyleSheet("""
            QPushButton { background-color: #37474f; }
            QPushButton:hover { background-color: #455a64; }
            QPushButton:pressed { background-color: #263238; }
        """)
        self.forward_btn.clicked.connect(lambda: self.seek_relative(5000))

        button_layout.addWidget(self.rewind_btn)
        button_layout.addWidget(self.toggle_btn)
        button_layout.addWidget(self.restart_btn)
        button_layout.addWidget(self.forward_btn)

        layout.addLayout(button_layout)

        progress_layout = QVBoxLayout()
        self.time_label = QLabel("00:00 / 00:00", self)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.progress_slider = ClickableSlider(Qt.Orientation.Horizontal, self)
        self.progress_slider.setRange(0, 0)
        self.progress_slider.sliderMoved.connect(self.set_position)
        self.progress_slider.sliderReleased.connect(
            lambda: self.set_position(self.progress_slider.value())
        )

        progress_layout.addWidget(self.time_label)
        progress_layout.addWidget(self.progress_slider)

        layout.addLayout(progress_layout)

        vol_layout = QHBoxLayout()
        vol_icon = QLabel("Audio Volume:", self)

        self.vol_slider = ClickableSlider(Qt.Orientation.Horizontal, self)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(50)
        self.vol_slider.valueChanged.connect(self.change_volume)

        vol_layout.addWidget(vol_icon)
        vol_layout.addWidget(self.vol_slider)

        layout.addLayout(vol_layout)
        self.setLayout(layout)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Q:
            QApplication.quit()
        super().keyPressEvent(event)

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Audio File", "", "MP3 Files (*.mp3)"
        )

        if file_path:
            if not file_path.lower().endswith(".mp3"):
                QMessageBox.critical(
                    self, "Invalid File", "Only .mp3 audio files are supported."
                )
                return

            self.player.setSource(QUrl.fromLocalFile(file_path))
            filename = os.path.basename(file_path)
            self.status_label.setText(f"Active MP3 File: {filename}")
            self.player.play()
            self.toggle_btn.setText("Pause")

    def toggle_playback(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.toggle_btn.setText("Play")
            self.status_label.setText("MP3 File Paused.")
        else:
            if self.player.source().isEmpty():
                self.upload_file()
            else:
                self.player.play()
                self.toggle_btn.setText("Pause")
                filename = os.path.basename(self.player.source().toLocalFile())
                self.status_label.setText(f"Playing MP3 File: {filename}")

    def restart_music(self):
        if not self.player.source().isEmpty():
            self.player.setPosition(0)
            self.player.play()
            self.toggle_btn.setText("Pause")
            filename = os.path.basename(self.player.source().toLocalFile())
            self.status_label.setText(f"Restarted MP3 File: {filename}")

    def seek_relative(self, offset_ms):
        current_pos = self.player.position()
        target_pos = max(
            0, min(self.player.duration(), current_pos + offset_ms)
        )
        self.player.setPosition(target_pos)

    def update_position(self, position):
        if not self.progress_slider.isSliderDown():
            self.progress_slider.setValue(position)
        self.update_time_label(position, self.player.duration())

    def update_duration(self, duration):
        self.progress_slider.setRange(0, duration)
        self.update_time_label(self.player.position(), duration)

    def set_position(self, position):
        self.player.setPosition(position)

    def change_volume(self, value):
        self.audio_output.setVolume(value / 100.0)

    def update_time_label(self, position_ms, duration_ms):
        pos_sec = position_ms // 1000
        dur_sec = duration_ms // 1000

        pos_str = f"{pos_sec // 60:02d}:{pos_sec % 60:02d}"
        dur_str = f"{dur_sec // 60:02d}:{dur_sec % 60:02d}"

        self.time_label.setText(f"{pos_str} / {dur_str}")


# --- Application Entry Point --- 
if __name__ == "__main__":
    
    app = QApplication(sys.argv)

    def launch_main_window():
        global main_window
        main_window = CobotControlHMI()
        main_window.show()

    intro = CyberCobotSplashScreen(on_finish_callback=launch_main_window)
    intro.show()

    sys.exit(app.exec())