def animate(x,y,fig,ax, interval=7, color='b'):
    tail = 20
    ln, = plt.plot([], [], 'o', c=color, alpha=0.8)

    def init():
        ax.set_xlim(-5000,5000)
        ax.set_ylim(-6000,6000)
        return ln,

    def update(frame):
        #print(frame)
        ln.set_data(x[max(0,frame-tail):frame], y[max(0,frame-tail):frame])
        return ln,

    ani = FuncAnimation(fig, update, frames=np.arange(len(x)),
                        init_func=init, blit=True, interval=interval)
