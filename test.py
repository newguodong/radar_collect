import matplotlib.pyplot as plt

def draw_rect(x, y, width, height, color):
    rectangle = plt.Rectangle((x, y), width, height, fc=color, ec='red', lw=1, alpha=0.1)

    fig, ax = plt.subplots()
    ax.add_patch(rectangle)

    plt.axis('equal')
    plt.show()

draw_rect(0.5,0.5,0.5,0.5, 'blue')