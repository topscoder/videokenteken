BENCHMARK ON SINGLE YOUTUBE VIDEO


VIDEO                   https://www.youtube.com/watch?v=EgoGzvcy45E
VIDEO DURATION          00:10:21

                        KAGGLE CPU          GOOGLE COLAB T4 GPU     KAGGLE GPU T4 x2
ANALYSIS DURATION                           0:05:05.350415          
AVG INFERENCE SPEED     70ms                6.5ms                   8ms



OPTIMISATION BATCH SIZES
====

BATCH SIZE              5                       10                  20
ANALYSIS DURATION       0:04:29.849164          0:04:12.225761      0:04:18.196626
AVG INFERENCE SPEED     9ms                     2.4ms               1.7ms



OPTIMISATION ASYNCHRONOUS LOADING
====

BATCH SIZE              10
ANALYSIS DURATION       0:03:55.899604
AVG INFERENCE SPEED     1.9ms


OPTIMISATION EASYOCR USING GPU
====

BATCH SIZE              10
ANALYSIS DURATION       0:01:04.082354
AVG INFERENCE SPEED     1.3ms



WITH TESSERACT OCR

Draft Session
GPU T4 x2 On
Session
2m
12 hours
Disk
2.5GiB
Max 57.6GiB
CPU
CPU
146.00%
RAM
1.8GiB
Max 29GiB
GPU
GPU
22.00%
GPU Memory
327MiB
Max 15GiB

WITH EASYOCR

Draft Session
GPU T4 x2 On
Session
1m
12 hours
Disk
2.6GiB
Max 57.6GiB
CPU
CPU
165.00%
RAM
2.1GiB
Max 29GiB
GPU
GPU
36.00%
GPU Memory
937MiB
Max 15GiB