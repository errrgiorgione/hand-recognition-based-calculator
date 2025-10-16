import cv2, time
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2) 
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

#constants
FINGERS_POINTS = {
    0: [2, 3, 4], #thumb points -> point 1 is also part of the thumb, but for easier use (easier understanding of whatever the thumb is opened or closed) it is ignored
    1: [5, 6, 7, 8],
    2: [9, 10, 11, 12],
    3: [13, 14, 15, 16],
    4: [17, 18, 19, 20] #little finger points
}
COMMANDS = {
    0: {
        "finger_points": [4, 8],  #points to check
        "operation": "+"
    },
    1: {
        "finger_points": [4, 12],
        "operation": "-"
    },
    2: {
        "finger_points": [4, 16],
        "operation": "*"
    },
    3: {
        "finger_points": [4, 20],
        "operation": "/"
    }
}
INSTRUCTIONS_MAP = {
    0: "Insert {numberN} number's {digitN} digit",
    1: "Insert operation",
    2: "Confirm expression",
    3: ''
}
NUMBER_OF_NUMBERS = 2
NUMBER_OF_DIGITS = 2
DELAY = 2 
RESET_DELAY = 5 #to reset the expression there is an higher delay
RESET_VALUE = 5
THRESHOLD = 10

#functions
def draw_text(img, text,
          font=cv2.FONT_HERSHEY_SIMPLEX,
          pos=(0, 0),
          font_scale=1,
          font_thickness=2,
          text_color=(255, 255, 255),
          text_color_bg=(0, 0, 0),
          lineType = cv2.LINE_AA,
          transparency  = 0.4
          ):

    overlay = img.copy()
    x, y = pos
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    text_w, text_h = text_size
    cv2.rectangle(overlay, pos, (x + text_w, y + text_h), text_color_bg, -1)
    image_new = cv2.addWeighted(overlay, transparency, img, 1 - transparency, 0)
    cv2.putText(image_new, text, (x , y + text_h + font_scale - 1), font, font_scale, text_color, font_thickness, lineType)

    return image_new
def are_points_almost_equal(p1: list, p2: list, abs_tol=THRESHOLD) -> bool:
    if len(p1) != len(p2): # ensure same dimensions
        return False
    for i in range(len(p1)):
        if abs(p1[i] - p2[i]) > abs_tol:
            return False
    return True

main_index = single_number_index = total = prev_digit = last_command_time = 0
numbers = [''] * NUMBER_OF_NUMBERS
digits = [0] * NUMBER_OF_DIGITS
operation = [None] * (NUMBER_OF_NUMBERS - 1)
skip_cycle = is_number_done = False
instructions = INSTRUCTIONS_MAP[0].format(digitN=1, numberN=1)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        continue
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    if results.multi_hand_landmarks and results.multi_handedness:
        skip_cycle = False
        prev_digit = digits[single_number_index]
        digits = [digits[i] if single_number_index > i or is_number_done else 0 for i in range(len(digits))]
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            label = handedness.classification[0].label # left or right hand
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            h, w, _ = frame.shape

            #check for any command
            finger_coordinates = {}
            if main_index < NUMBER_OF_NUMBERS:
                for command in list(COMMANDS.values()):
                    for finger in command["finger_points"]:
                        landmark = hand_landmarks.landmark[finger]
                        cx, cy = int(landmark.x * w), int(landmark.y * h)
                        finger_coordinates[finger] = (cx, cy)
                    if are_points_almost_equal(finger_coordinates[command["finger_points"][0]], finger_coordinates[command["finger_points"][1]]): 
                        current_time = time.time()
                        if current_time - last_command_time > DELAY: #adding a little DELAY
                            digits[single_number_index] = prev_digit 
                            if is_number_done:
                                try: operation[main_index] = command["operation"] if not operation[main_index] else operation[main_index] 
                                except IndexError: pass #main_index always iterate one time more than len(operation)
                                for x in range(len(digits)): numbers[main_index] += str(digits[x])
                                main_index+=1
                                single_number_index = 0
                                is_number_done = False
                                if main_index != NUMBER_OF_NUMBERS: instructions = INSTRUCTIONS_MAP[0].format(digitN=single_number_index+1, numberN=main_index+1)
                                else: instructions = INSTRUCTIONS_MAP[3]
                            else:
                                if single_number_index == (NUMBER_OF_DIGITS - 1): 
                                    if main_index == (NUMBER_OF_NUMBERS - 1): instructions = INSTRUCTIONS_MAP[2]
                                    else: instructions = INSTRUCTIONS_MAP[1]
                                    is_number_done = True
                                else: 
                                    single_number_index += 1
                                    instructions = INSTRUCTIONS_MAP[0].format(digitN=single_number_index+1, numberN=main_index+1)
                                skip_cycle = True
                            last_command_time = time.time()
                        break
            
            if skip_cycle: continue

            # check thumb (right - left)
            thumb_finger = FINGERS_POINTS[0]
            thumb_first_point_coords = hand_landmarks.landmark[thumb_finger[0]]
            thumb_last_point_coords = hand_landmarks.landmark[thumb_finger[-1]]
            
            thumb_first_point_cx, thumb_last_point_cx = int(thumb_first_point_coords.x * w), int(thumb_last_point_coords.x * w)
            if (label.startswith("R") and thumb_last_point_cx < thumb_first_point_cx) or (label.startswith("L") and thumb_last_point_cx > thumb_first_point_cx): 
                if not is_number_done: digits[single_number_index] += 1
                cy = int(thumb_last_point_coords.y * h)
                cv2.circle(frame, (thumb_last_point_cx, cy), 8, (0, 0, 255), -1)

            # check all other fingers (top - bottom)
            for x in range(1, len(list(FINGERS_POINTS.values()))): #ignore thumb finger
                finger = FINGERS_POINTS[x]
                finger_first_point_coords = hand_landmarks.landmark[finger[0]]
                finger_last_point_coords = hand_landmarks.landmark[finger[-1]]
                
                first_point_cy, last_point_cy = int(finger_first_point_coords.y * h), int(finger_last_point_coords.y * h)
                if last_point_cy < first_point_cy:
                    if not is_number_done: digits[single_number_index] += 1
                    cx = int(finger_last_point_coords.x * w)
                    cv2.circle(frame, (cx, last_point_cy), 8, (0, 0, 255), -1)
                    
            # reset 
            if RESET_VALUE in digits and total:
                current_time = time.time()
                if current_time - last_command_time > RESET_DELAY: 
                    total = main_index = prev_digit = 0
                    operation = [None] * (NUMBER_OF_NUMBERS - 1)
                    numbers = [''] * NUMBER_OF_NUMBERS
                    instructions = INSTRUCTIONS_MAP[0].format(digitN=1, numberN=1)

    #create texts on the frame
    expression = ''
    for x in range(len(numbers)):
        number = numbers[x]
        if not number and main_index == x:
            number = ''
            for digit in digits: number += str(digit)
        if x > 0: expression += f"{operation[x-1]} " if operation[x-1] else ''
        expression += f"{number} "
    if main_index == NUMBER_OF_NUMBERS and numbers[NUMBER_OF_NUMBERS-1]: 
        total = eval(expression)
        expression += f"= {total}"

    image_new = draw_text(frame, expression, pos=(30, 30))
    image_new = draw_text(image_new, instructions, pos=(30, 430))
    cv2.imshow("Hand Recognition", image_new)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()