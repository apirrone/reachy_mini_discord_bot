Link to the blog post : https://huggingface.co/blog/pollen-robotics/make-and-publish-your-reachy-mini-apps

# Make and publish your Reachy Mini App


![image](https://cdn-uploads.huggingface.co/production/uploads/6303eb57fc783bfc74434dd9/QefLtqWGVCqcXNSy9dt5g.png)


*Build, package, and publish an app that the entire Reachy Mini community can install in one click - share your creations, inspire others, and contribute to the ecosystem!*

## Who this guide is for?

This guide is for developers who have **an idea or prototype for a Reachy Mini app** and want to **share it with the community**. It walks you through the process of packaging, testing, and publishing your app with minimal friction.

This guide focuses on the **Python SDK**, but you can also create apps using other approaches, such as the [web API](https://github.com/pollen-robotics/reachy_mini?tab=readme-ov-file#using-the-rest-api) / JavaScript templates.

*Looking for inspiration or examples? Explore [existing Reachy Mini apps](https://huggingface.co/spaces/pollen-robotics/Reachy_Mini_Apps) to see the kind of interactions and behaviors you can build and share.*

## **Turn your idea into a shareable app**

To make your python code into a Reachy Mini App, you basically need to:

1. Call your app logic from a specific run method (so we can start/stop it on demand)
2. Wrap it as a python package (so other users can install it)
3. And publish it as a space to share it with the community!

You don’t have to set this up manually: the Reachy Mini App Assistant can generate all the boilerplate for you and prepare your app for publishing!

## Let’s get started!

### Create the app template

We assume here that you’ve already installed the reachy-mini package into your Python environment. If it’s not the case check [this documentation](https://github.com/pollen-robotics/reachy_mini?tab=readme-ov-file#installation-of-the-daemon-and-python-sdk) first.

The app-assistant tool directly comes with your reachy-mini installation. So, to create everything needed for your app, simply run from your terminal:

```python
reachy-mini-app-assistant create
```

It will ask you to provide a name for your app, the destination path, etc.

```bash
~$ reachy-mini-app-assistant create
$ What is the name of your app ?
? > reachy_mini_hello_world

$ Choose the language of your app
? > python

$ Where do you want to create your app project ?
? > ~/my_reachy_mini_apps/
✅ Created app 'reachy_mini_hello_world' in ~/my_reachy_mini_apps/reachy_mini_hello_world/
```

Once done, it will generate the following project structure:

```
reachy_mini_hello_world/
├── index.html
├── pyproject.toml
├── reachy_mini_hello_world
│   ├── __init__.py
│   └── main.py
├── README.md
└── style.css
```

You can see a few different things here.

1. First, the python package itself (indented with `>` files below). This is where you will add your logic. You can see both the python entry point and an optional webpage to provide a settings page for your app. We’ll detail this part in the next section.


  ```
  reachy_mini_hello_world/
  ├── index.html
  ├── pyproject.toml
  ├── reachy_mini_hello_world
  │   ├── __init__.py
  │   └── main.py
  ├── README.md
  └── style.css
  ```
    
2. The front page for your Hugging Face Space and some metadata to make it easily discoverable.

```
reachy_mini_hello_world/
>├── index.html
├── pyproject.toml
├── reachy_mini_hello_world
│   ├── __init__.py
│   └── main.py
>├── README.md
>└── style.css
```

### Write your app logic

Your app inherits from `ReachyMiniApp`. When started from the dashboard, it runs in a background thread. Use the provided `stop_event` to exit cleanly.

```python
import threading

from reachy_mini import ReachyMini, ReachyMiniApp
from reachy_mini.utils import create_head_pose

class ReachyMiniHelloWorld(ReachyMiniApp):
    # Optional: URL to a custom configuration page for the app
    # For example: http://localhost:5173
    custom_app_url: str | None = None

    def run(self, reachy_mini: ReachyMini, stop_event: threading.Event):
        # Write your code here
        # ReachyMini is already initialized and connected
        # Check the stop_event to gracefully exit the loop
        # Example:
        # import time
        # import numpy as np
        #
        # t0 = time.time()
        #
        # while not stop_[event.is](http://event.is)_set():
        #     t = time.time() - t0
        #
        #     yaw = 30 * np.sin(2 * np.pi * 0.5 * t)
        #     head_pose = create_head_pose(yaw=yaw, degrees=True)
        #
        #     reachy_mini.set_target(head=head_pose)
        #
        #     time.sleep(0.01)

        print("This is a placeholder for your app logic.")
```

<details>
<summary>Make a web UI for your app</summary>

If you want, you can make a web UI for your app. This can be a settings page, some kind of visualization, enable disable some stuff, whatever you want really !

To do that, you have to set a `custom_app_url` your app (`None` by default). If this is set, the app will run a `FastAPI` webserver that will serve what’s inside the `static` directory inside your python module. 

```bash
reachy_mini_hello_world/
├── index.html
├── pyproject.toml
└── reachy_mini_hello_world
|   ├── __init__.py
|   ├── main.py
|   └── static
|       ├── index.html
|       ├── main.js
|       └── style.css
├── [README.md](http://README.md)
└── style.css
```

We’ve included a minimal example of how that works when you create a new app with the assistant. You can also take a look at it here https://huggingface.co/spaces/pollen-robotics/reachy_mini_template_app

</details>

### Test before publishing

- Execute `main.py` manually in your environment
- Test your app locally through the dashboard
    - With your Reachy Mini python environment activated, navigate to your app and run `pip install -e .`
    - Run the daemon : `reachy-mini-daemon`
    - In your browser, go to `http://127.0.0.1:8000/`
    - Your app will show up in the installed applications
---

### Publish your app

```bash
~$ reachy-mini-app-assistant publish
$ What is the local path to the app you want to publish?
? > ~/my_reachy_mini_apps/reachy_mini_hello_world/
Do you want your space to be created private or public?
? > private
✅ App published successfully.
```

You should now see your app on your HuggingFace account https://huggingface.co/spaces/hf_username/reachy_mini_hello_world

### Request your app to be added to the official apps

If you think your app is production ready, you can request it to be added to the list of official apps that appear in the dashboard ! Just make sure it’s public before submitting it.

Just run : 

```bash
~$ reachy-mini-app-assistant publish --official
```

This will create a PR on [this dataset](https://huggingface.co/datasets/pollen-robotics/reachy-mini-official-app-store).

Please make sure to briefly explain what your app does. The Pollen and Hugging Face team will review your request.

---

### Dashboard UI overview
![Capture d’écran du 2025-11-21 17-15-25](https://cdn-uploads.huggingface.co/production/uploads/6303eb57fc783bfc74434dd9/vsuRnskDVEL3erRVa0cJh.png)

- Install from Hugging Face: official apps you can install with the Install button
- Applications: apps already installed locally
- Each app tile indicates status and actions like Run and Stop
- Click on the ⚙️ icon of a running app to view its GUI