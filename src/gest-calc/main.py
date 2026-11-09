"""Calculadora controlada por gestos de la mano (MediaPipe Hands)."""
import time

import cv2
import mediapipe as mp

from calculator import Calculator
from gestures import fingers_up, classify, Smoother, HoldConfirmer

CAMERA_INDEX = 0
WINDOW = "Calculadora por gestos (q para salir)"
HELP = ("2 manos: suma de dedos=digito | 1 dedo:+  2:-  3:x  4:/  palma:=  "
        "pulgar:borrar  menique:reset")


def apply_action(calc, label):
    if label.startswith("DIGIT_"):
        calc.press_digit(int(label.split("_")[1]))
    elif label in ("+", "-", "*", "/"):
        calc.press_op(label)
    elif label == "=":
        calc.equals()
    elif label == "DELETE":
        calc.delete()
    elif label == "RESET":
        calc.reset()


def draw_ui(frame, calc, label, progress):
    h, w = frame.shape[:2]
    cv2.rectangle(frame, (0, 0), (w, 110), (30, 30, 30), -1)
    cv2.putText(frame, calc.expression, (15, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 200, 200), 2)
    cv2.putText(frame, calc.display, (15, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 1.6, (255, 255, 255), 3)
    cv2.putText(frame, f"Gesto: {label or '-'}", (15, h - 45),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.rectangle(frame, (15, h - 35), (15 + int(250 * progress), h - 20),
                  (0, 255, 0), -1)
    cv2.rectangle(frame, (15, h - 35), (265, h - 20), (255, 255, 255), 1)
    cv2.putText(frame, HELP, (15, h - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)


def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise SystemExit("No se pudo abrir la camara (indice %d)" % CAMERA_INDEX)

    mp_hands = mp.solutions.hands
    drawer = mp.solutions.drawing_utils
    hands = mp_hands.Hands(max_num_hands=2, model_complexity=0,
                           min_detection_confidence=0.7,
                           min_tracking_confidence=0.6)
    calc, smoother, confirmer = Calculator(), Smoother(), HoldConfirmer()

    # Pantalla completa (NUEVO)
    cv2.namedWindow(WINDOW, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(WINDOW, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        result = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        fingers = []
        if result.multi_hand_landmarks:
            for hand in result.multi_hand_landmarks:
                drawer.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
                fingers.append(fingers_up(hand.landmark))

        label = smoother.update(classify(fingers))
        confirmed, progress = confirmer.update(label, time.monotonic())
        if confirmed:
            apply_action(calc, confirmed)

        draw_ui(frame, calc, label, progress)
        cv2.imshow(WINDOW, frame)
        if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
            break

    cap.release()
    hands.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
