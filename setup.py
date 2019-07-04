import os

try:
    from orbis.core.addon_setup import AddonSetupBaseClass
    AddonSetupBaseClass().run(os.path.dirname(os.path.realpath(__file__)))
except Exception as exception:
    print("Orbis not found. Please install Orbis first.")
    print(f"({exception})")
