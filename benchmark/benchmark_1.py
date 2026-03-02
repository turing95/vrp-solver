from time import process_time

from benchmark.sample import load_instance
from routing import Policy


if __name__ == '__main__':
    with open('./benchmark/results/results_1.csv', 'w') as f:
        f.write('run,cpu-time,obj-function\n')

        for run in range(1, 11):
            instance = load_instance()
            policy = Policy(instance)

            start_time = process_time()
            solution = policy.route()
            end_time = process_time()

            f.write(f'{run},{end_time - start_time},{solution.compute_cost()}\n')
            f.flush()
