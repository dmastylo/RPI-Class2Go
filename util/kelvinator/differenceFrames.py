import sys
import os

from scipy.misc import imread
from scipy.linalg import norm
from scipy import sum, average

def createManifest(keepList, keepIndicies, frameRate):
    outfile = "jpegs/manifest.txt"
    FILE = open(outfile, "w")
    timeBetweenFrames = 1.0/float(frameRate)
    index = 0
    FILE.write("{")
    print len(keepList)
    print len(keepIndicies)

    while(index < len(keepList)):
        FILE.write("\"")
        toWrite = str(keepIndicies[index] * timeBetweenFrames)
        FILE.write(toWrite)
        FILE.write("\":{\"imgsrc\":\"")
        FILE.write(keepList[index])
        FILE.write("\"}")
        if index < len(keepList)-1:
            FILE.write(",")
        index += 1

    FILE.write("}")


def main():
    #Set the threshold for diff from argument passed
    threshold = float(sys.argv[1])
    #Read in all the files names in jpegs folders as a list of strings
    imageList = os.listdir("./jpegs")
    imageList.sort()
    keepList = []
    keepIndicies = []
    deleteList = []
    outfile = "toDelete.txt"
    index = 0
    #The first image is always kept
    keepList.append(imageList[index])
    keepIndicies.append(0)
    #If a large enough difference is recognized between frames, the next frame is kept, otherwise it is deleted
    while index < len(imageList)-1:
    	  diff = computeDiff("./jpegs/"+imageList[index], "./jpegs/"+imageList[index+1])
    	  print diff
    	  if diff > threshold:
    	      keepList.append(imageList[index+1])
              keepIndicies.append(index+1)
    	  else:
    	      deleteList.append(imageList[index+1])
    	  index += 1

    #Write out to the list of images that should be deleted
    FILE = open(outfile, "w")
    for image in deleteList:
    	  FILE.write(image)
    	  FILE.write("\n")

    createManifest(keepList, keepIndicies, sys.argv[2])
    print keepList

def computeDiff(file1, file2):
    # read images as 2D arrays (convert to grayscale for simplicity)
    img1 = to_grayscale(imread(file1).astype(float))
    img2 = to_grayscale(imread(file2).astype(float))
    # compare
    n_m, n_0 = compare_images(img1, img2)
    return n_m*1.0/img1.size

def compare_images(img1, img2):
    # normalize to compensate for exposure difference, this may be unnecessary
    # consider disabling it
    img1 = normalize(img1)
    img2 = normalize(img2)
    # calculate the difference and its norms
    diff = img1 - img2  # elementwise for scipy arrays
    m_norm = sum(abs(diff))  # Manhattan norm
    z_norm = norm(diff.ravel(), 0)  # Zero norm
    return (m_norm, z_norm)


def to_grayscale(arr):
    "If arr is a color image (3D array), convert it to grayscale (2D array)."
    if len(arr.shape) == 3:
        return average(arr, -1)  # average over the last axis (color channels)
    else:
        return arr

def normalize(arr):
    rng = arr.max()-arr.min()
    amin = arr.min()
    return (arr-amin)*255/rng

if __name__ == "__main__":
    main()





