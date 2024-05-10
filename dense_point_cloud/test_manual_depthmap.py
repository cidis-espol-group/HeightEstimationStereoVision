import os
import sys
import numpy as np
import cv2 as cv; cv2 = cv
 
imgL = cv2.imread('image_l.png', 0)
imgR = cv2.imread('image_r.png', 0)

# Aplicar el filtro bilateral
sigma = 1.5  # Parámetro de sigma utilizado para el filtrado WLS.
lmbda = 8000.0  # Parámetro lambda usado en el filtrado WLS.


blockSize = 11
min_disparity = 10
max_disparity = 170
P1 = 8
P2 = 32

stereo = cv2.StereoSGBM_create(
	# minDisparity=min_disparity,
	numDisparities=(max_disparity - min_disparity),
	blockSize=blockSize,
	P1=3*blockSize*blockSize * P1,
	P2=3*blockSize*blockSize * P2,
	disp12MaxDiff=0,
	preFilterCap=0,
	uniquenessRatio=10,
#	speckleWindowSize=100,
#	speckleRange=1,
#	mode=cv.StereoSGBM_MODE_SGBM
# 	mode=cv.StereoSGBM_MODE_HH
	mode=cv.StereoSGBM_MODE_SGBM_3WAY
)




def redraw():
	
	# Calcular el mapa de disparidad de la imagen izquierda a la derecha
	left_disp = stereo.compute(imgL, imgR).astype(np.float32) / 16.0

	# Crear el matcher derecho basado en el matcher izquierdo para consistencia
	right_matcher = cv2.ximgproc.createRightMatcher(stereo)

	# Calcular el mapa de disparidad de la imagen derecha a la izquierda
	right_disp = right_matcher.compute(imgR, imgL).astype(np.float32) / 16.0

	# Crear el filtro WLS y configurarlo
	wls_filter = cv2.ximgproc.createDisparityWLSFilter(matcher_left=stereo)
	wls_filter.setLambda(lmbda)
	wls_filter.setSigmaColor(sigma)

	# Filtrar el mapa de disparidad utilizando el filtro WLS
	filtered_disp = wls_filter.filter(left_disp, imgL, disparity_map_right=right_disp)

	# Normalización para la visualización o procesamiento posterior
	filtered_disp = cv2.normalize(src=filtered_disp, dst=filtered_disp, beta=0, alpha=255, norm_type=cv2.NORM_MINMAX)
	filtered_disp = np.uint8(filtered_disp)

	cv.imshow("out", filtered_disp)


def on_blockSize(pos):
	global blockSize
	blockSize = 1 - (1 - pos) // 2 * 2
	stereo.setBlockSize(blockSize)
	redraw()

def on_mindisparity(pos):
	global min_disparity
	min_disparity = pos
	stereo.setMinDisparity(min_disparity)
	stereo.setNumDisparities(max_disparity - min_disparity)
	redraw()

def on_maxdisparity(pos):
	global max_disparity
	max_disparity = pos
	stereo.setNumDisparities(max_disparity - min_disparity)
	redraw()

def on_P1(pos):
	global P1
	P1 = pos
	stereo.setP1(3*blockSize*blockSize * P1)
	redraw()

def on_P2(pos):
	global P2
	P2 = pos
	stereo.setP2(3*blockSize*blockSize * P2)
	redraw()

def set_disp12MaxDiff(pos):
	stereo.setDisp12MaxDiff(pos)
	redraw()

def set_preFilterCap(pos):
	stereo.setPreFilterCap(pos)
	redraw()


cv.namedWindow("out", cv2.WINDOW_NORMAL)
cv.resizeWindow("out",600, 600)
cv.createTrackbar("blockSize", "out", blockSize, 51, on_blockSize)
cv.createTrackbar("minDisparity", "out", min_disparity, 200, on_mindisparity)
cv.createTrackbar("maxDisparity", "out", max_disparity, 200, on_maxdisparity)
cv.createTrackbar("P1", "out", P1, 64, on_P1)
cv.createTrackbar("P2", "out", P2, 64, on_P2)
cv.createTrackbar("disp12MaxDiff", "out", 0, 100, set_disp12MaxDiff)
cv.createTrackbar("preFilterCap", "out", 0, 63, set_preFilterCap)



redraw()
while True:
	key = cv.waitKey()
	if key == -1:
		break
	print(key)