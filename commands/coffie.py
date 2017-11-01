import random
import time
import zlib

class Coffie():

    @classmethod
    def who(cls, seed, people=None):
        people = (people.split(',') if people else ('Mats', 'Paul', 'Olaf'))
        random.seed(int(zlib.crc32(seed.encode())) + random.randrange(1, 1000))
        time.sleep(random.randrange(1, 10000) / 100000)
        person = cls.generate_person(people)
        if people.__len__() > 2:
            fp = open('/tmp/last_person', 'a+')
            fp.seek(0)
            last_person = fp.read()
            yield('Last person %s' % last_person)
            if last_person.__len__() > 0:
                if last_person == person:
                    while last_person == person:
                        person = generate_person()
            fp.truncate(0)
            fp.write(person)
            fp.flush()
            fp.close()
        yield('%s is getting the coffie' % person)

    @classmethod
    def benchmark(cls, seed=None, people=None):
        import numpy as np
        import matplotlib.pyplot as plt
        import matplotlib.animation as anim

        people = sorted((people.split(',') if people else ('Mats', 'Paul', 'Olaf')))
        random.seed(int(zlib.crc32(seed.encode())) + random.randrange(1, 1000))
        time.sleep(random.randrange(1, 10000) / 100000)

        results = {}
        for p in people:
            results[p] = 0

        fig, ax = plt.subplots()

        sorted_keys = sorted(results.keys())

        def go(i):
            for iz in range(9000):
                results[cls.generate_person(people)] += 1
            ax.clear()
            ax.plot(sorted_keys, [results[key] for key in sorted_keys])

        a = anim.FuncAnimation(fig, go, repeat=False, save_count=2, interval=20, blit=False)
        plt.show()

    @staticmethod
    def generate_person(people):
        return random.choice(people)