import sqlite3

def printtable():
    cursor.execute("SELECT * FROM ssim")
    rows = cursor.fetchall()
    for row in rows:
        for value in row:
            print value,
        print ''

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

try:
    cursor.execute("DROP TABLE ssim")
except:
    pass

try:
    cursor.execute("CREATE TABLE ssim (image_one text, image_two text, unique(image_one,image_two))")
except:
    pass
'''
try:
    cursor.execute("CREATE INDEX indx1 ON ssim(pair_name)")
except:
    pass
'''
printtable()

conn.commit()

conn.close()

print "DONE"

'''
for i in xrange(500):
    if i%2 == 1:
        for j in xrange(10):
            print str(i)+'-'+str(2**j)
'''
