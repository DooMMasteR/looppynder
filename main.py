import imagehash
from PIL import Image, ImageSequence

gif = Image.open('test.gif')
gif_seq = ImageSequence.Iterator(gif)

framecounter = 0
for image in gif_seq:
    framecounter += 1

print('Sequence has ' + str(framecounter) + ' frames.')

gif_seq = ImageSequence.Iterator(gif)
image_hashes = []
counter = 1
for image in gif_seq:
    image_hashes.append(imagehash.phash(image, 24))

counter1 = 0
diffmap = []
for hash1 in image_hashes:
    counter2 = 0
    counter1 += 1
    for hash2 in image_hashes:
        counter2 += 1
        difference = hash1 - hash2
        diffmap.append([[counter1, counter2], difference])

filtered_diffmap = []
for frame in diffmap:
    if frame[0][0] != frame[0][1] and frame[0][1] - frame[0][0] > 20 and frame[1] < 35:
        filtered_diffmap.append(frame)

del image
del image_hashes
del gif
del gif_seq
del diffmap
filtered_diffmap.sort(key=lambda tup: tup[0][1] - tup[0][0])

print("Start \t End \t Dur \t Diff")
for frame in filtered_diffmap:
    print(str(frame[0][0]).ljust(4), "\t", str(frame[0][1]).ljust(4), "\t", str(frame[0][1] - frame[0][0]), "\t",
          str(frame[1]))
