from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="APP",
    settings_files=['/code/app/modules/settings.yaml'],
    
)
