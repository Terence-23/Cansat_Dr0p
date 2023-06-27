import time

input("press enter to save timestamp")
t1 = time.time()
print(t1)
print(time.ctime(t1))

input("press enter to save timestamp")
t2 = time.time()
print(t2)
print(time.ctime(t2))

print(f"deltatime: {t2-t1}")

