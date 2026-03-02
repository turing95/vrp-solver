import matplotlib.pyplot as plt

from routing.entity.constant import NONE_TASK
from routing import Instance

colors = ['red', 'green', 'blue', 'lime', 'slateblue', 'chocolate', 'brown', 'coral', 'orange', 'cyan',
          'steelblue', 'orchid', 'magenta', 'navy']


def get_instance_figure(instance: Instance):
    coordinates = [t.coordinates for t in instance.tasks.values()]
    x, y = zip(*coordinates)

    fig, ax = plt.subplots()

    # Plot the points
    ax.scatter(x, y, s=2)

    def plot_segment(a, b, color, linestyle):
        ax.plot([a[0], b[0]], [a[1], b[1]], c=color, linestyle=linestyle)

    # Plot the routes
    for j_id, j in instance.plan.jobs.items():
        # task coordinates
        coordinates = [instance.get_coordinates(t_id) for t_id in j.task_ids]
        executing_task = instance.plan.executing_task[j_id]

        executing_task_pos = 0
        color = colors[j_id % len(colors)]

        if executing_task != NONE_TASK:
            executing_task_pos = j.task_ids.index(executing_task)
            for point_a, point_b in zip(coordinates[0:executing_task_pos], coordinates[1:executing_task_pos+1]):
                plot_segment(point_a, point_b, color, 'dotted')

        for point_a, point_b in zip(coordinates[executing_task_pos:-1], coordinates[executing_task_pos+1:]):
            plot_segment(point_a, point_b, color, 'solid')

    fig.suptitle(f"Instance at time {instance.plan.current_time}", fontsize=16)
    return fig
