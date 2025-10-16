# About

This repository contains a single-file Python hand-based calculator made with `cv2` and `mediapipe` Python modules. As suggested by the name, this calculator uses hands gestures to find the numbers and the operations to create a mathematical expression.

# Usage

## Download

To download and use this script you can download the entire repository using `git clone` and download all the required modules using `pip` (`cv2` and `mediapipe` module).

```
git clone https://github.com/errrgiorgione/hand-recognition-based-calculator
cd hand-recognition-based-calculator
pip install -r requirements.txt
```

Once you download the modules, you can run the script using the following command:

```
python hand_recognition.py
```

> [!NOTE]
> The script was tested on a Windows 11 computer using Python 3.10.0 and using the modules' version indicated in the [requirement](https://github.com/errrgiorgione/hand-recognition-based-calculator/blob/main/requirements.txt) file.

## Numbers and operations

The script allows a maximum of two hands simultaneously, meaning any other hand won't be taken into account.
You can show either one hand or both hands, and the script will understand the number you are showing based on your fingers' position. The hand is supposed to stay with the **palm of the hand facing the camera**, the **thumb finger pointing to one of the sides** and the **other fingers pointing upwards**.

The following image shows how the hand is seen by the script, and it is essential to understand how the script counts the fingers.

<img width="585" height="538" alt="hand_coordinates_Image" src="https://github.com/user-attachments/assets/cf8ecb61-aac1-4aa5-b212-d2cf6e379bea" />

The script takes the **y coordinate** of the first and last point of each finger, whereas the first point is the nearest point to the palm of the hand and the last point is the furthest away point from the palm of the hand.
When the y coordinate of the finger's last point is higher than the y coordinate of the finger's first point the script adds one to the `digits[i]` variable.

This method works for all the fingers **except for the _thumb fingers_** which are counted using their **x coordinate**. Therefore, the thumb fingers will be counted only when the thumb's first point is closer to the 0th point than the thumb's last point.

Each number of the mathematical expression must have the **same number of digits**.
The number of numbers and the number of digits for each number must be specified before running the script by modifying the `NUMBER_OF_NUMBERS` and `NUMBER_OF_DIGITS` constants.

With the current method of finger counting, you can indicate any number included in the range 1-10 and the script will ask you to indicate a new number for `NUMBER_OF_DIGITS` times before finishing a number, starting from the most significant digit to the least significant digit (example: from hundreds to units).
To confirm the digit, you must close your thumb finger with any other finger of your liking. The `are_points_almost_equal` function is responsible for this job, and it uses the `THRESHOLD` constant as a margin to understand when the thumb finger is closing with another finger. By default, it is set to `10`, but you can change it and the higher it is, the more often the function will return `True` but it will also lead to more frequent misunderstandings.

Once the number has been completed (all the digits have been detected), the script will ask you for the operation. This calculator can do the 4 basic mathematical operations: _addition, subtraction, multiplication and division_. At this stage, how you close your finger will indicate the operation:

- Thumb + index finger = addition
- Thumb + middle finger = subtraction
- Thumb + ring finger = multiplication
- Thumb + little finger = division

Once the operation has been specified by the user, the script will ask for the new number's digits, following the previously illustrated rules. This cycle repeats for `NUMBER_OF_NUMBERS` times and once it's done it will ask the user to confirm the expression by closing the thumb with any other finger. Finally, it will show the result of the mathematical expression.

Between any of these operations, there is a delay to avoid the script taking multiple inputs (example: multiple digits) too quickly. The delay is specified by the `DELAY` constant, which is set to 2 seconds by default.
Once the expression has been solved and showed by the script, a different, longer delay will start: the `RESET_DELAY`, which is 5 seconds long by default. Once this delay ends, the user can show an open hand to the camera to reset the calculator and start writing another expression. Keep in mind that the new expression will have the same
value of `NUMBER_OF_NUMBERS` and `NUMBER_OF_DIGITS` as the one before.

> [!NOTE]
> Even though it is tecnhically possible, it is very hard to indicate 0 as there is an high chance that the thumb finger will close with another finger before the script counts 0 fingers.

## Instructions

To help the user using the calculator, instructions can be found in the bottom left corner of the script's window.
The instructions will change over time and will guide the user through their experience.
