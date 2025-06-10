from matplotlib.widgets import Slider, CheckButtons  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import yaqc  # type: ignore
import numpy as np


def main(port, address):
    cam = yaqc.Client(port=port, address=address)

    x = cam.get_mappings()["xindex"]
    y = cam.get_mappings()["yindex"]

    fig, (ax, opt1, opt2, opt3) = plt.subplots(nrows=4, height_ratios=[10, 1, 1, 1])

    try:
        y0 = cam.get_measured()["mean"]
    except KeyError:
        y0 = np.zeros((x*y).shape)
    art = ax.matshow(y0)

    integration = Slider(opt1, "integration time", 3000, 1e6, valinit=cam.get_integration_time_micros())
    acquisition = Slider(opt2, "acquisitions (2^x)", 0, 8, valinit=0, valstep=1)
    measure_button = CheckButtons(opt3, labels=["call measure"], label_props=dict(fontsize=[20]))

    state = {
        "current" : 0,
        "next" : 0
    }


    def update_line(ydata):
        l.set_ydata(ydata)
        ax.relim()
        ax.autoscale_view()
        fig.canvas.draw_idle()


    def submit(measure=False):
        try:
            if "call measure" in measure_button.get_checked_labels() \
                or measure:
                    if state["current"] >= state["next"]:
                        state["next"] = cam.measure()
            measured = cam.get_measured()
            y = measured["mean"][sl]
            state["current"] = measured["measurement_id"]
            update_line(y)
        except ConnectionError:
            pass


    submit(measure=True)
    timer = fig.canvas.new_timer(interval=200)


    @timer.add_callback
    def update():
        submit()


    def update_integration_time(arg):
        cam.set_integration_time_micros(arg)


    def update_acquisition(arg):
        cam.set_acquistion(2**arg)


    integration.on_changed(update_integration_time)
    acquisition.on_changed(update_acquisition)

    plt.tight_layout()
    timer.start()
    plt.show()
