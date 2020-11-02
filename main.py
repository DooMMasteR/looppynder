import imagehash
import sqlite3
from PIL import Image, ImageSequence
import numpy as np
import io
import time


start = time.time()
def adapt_array(arr):
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())


def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)

sqlite3.register_adapter(np.ndarray, adapt_array)
sqlite3.register_converter("array", convert_array)

mem_db = sqlite3.connect("file::memory:?cache=shared", detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False, uri=True)
gif = Image.open('test.gif')
gif_seq = ImageSequence.Iterator(gif)
mem_db.execute('CREATE TABLE frame_data(id INTEGER PRIMARY KEY ASC, phash array, dhash array)')
mem_db.execute(
    'CREATE TABLE matches(id INTEGER PRIMARY KEY ASC, start INTEGER, end INTEGER, pdiff INTEGER, ddiff INTEGER, '
    'FOREIGN KEY(start) REFERENCES frame_data(id), FOREIGN KEY(end) REFERENCES frame_data(id))')
mem_de_cursor1 = mem_db.cursor()
mem_de_cursor2 = mem_db.cursor()

framecounter = 0
for image in gif_seq:
    framecounter += 1

print('Sequence has ' + str(framecounter) + ' frames.')
print('Init took : ', str((time.time() - start)*1000), 'ms' )
start = time.time()
gif_seq = ImageSequence.Iterator(gif)
counter = 0
hashes = []
for image in gif_seq:
    counter += 1
    hashes.append([counter, imagehash.phash(image, 24).hash, imagehash.dhash(image, 24).hash])

print('Hashing took : ', str((time.time() - start)*1000), 'ms' )

mem_de_cursor1.executemany('INSERT INTO frame_data VALUES (?,?,?)',
                           hashes)
print('Hashing with insert took : ', str((time.time() - start)*1000), 'ms' )


start = time.time()

counter1 = 0
diffmap = []
for (id1, phash1, dhash1) in hashes:
    counter2 = 0
    counter1 += 1
    mem_de_cursor2.execute('SELECT * FROM frame_data')
    for (id2, phash2, dhash2) in hashes:
        counter2 += 1
        if counter1 >= counter2:
            continue
        diffmap.append([id1, id2, abs(imagehash.ImageHash(phash1) - imagehash.ImageHash(phash2)),
                        abs(imagehash.ImageHash(dhash1) - imagehash.ImageHash(dhash2))])

print('Making differences took : ', str((time.time() - start)*1000), 'ms' )

mem_db.executemany("INSERT INTO matches VALUES (null, ?, ?, ?, ?)", diffmap)

print('Making differences with insert took : ', str((time.time() - start)*1000), 'ms' )
del diffmap
del hashes

mem_de_cursor1.execute(
    "SELECT * FROM (SELECT * FROM matches WHERE (end - start) > 10  AND (ddiff < 200 OR pdiff < 200) ORDER BY ddiff "
    "ASC, pdiff ASC LIMIT 25) ORDER BY ddiff DESC, pdiff DESC")
for frame in mem_de_cursor1:
    print(frame)
