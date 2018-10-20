import wiki
from core.conftest import *  # noqa: F401, F403
from core.conftest import PLUGINS, POPULATORS
from wiki.test_data import WikiPopulator

PLUGINS.append(wiki)
POPULATORS.append(WikiPopulator)
