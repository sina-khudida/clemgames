"""
Generate instances for the taboo game.

usage:
python3 instancegenerator.py
Creates instance.json file in ./in

"""
import os
import random
import logging
from tqdm import tqdm

from clemcore.clemgame import GameInstanceGenerator

N_INSTANCES = 20  # how many different target words; zero means "all"
N_GUESSES = 3  # how many tries the guesser will have
N_RELATED_WORDS = 3
LANGUAGE = "en"
VERSION = "v1.5"

logger = logging.getLogger(__name__)

random.seed(42)

class TabooGameInstanceGenerator(GameInstanceGenerator):

    def __init__(self):
        super().__init__(os.path.dirname(__file__))

    def on_generate(self):
        for frequency in ["high", "medium", "low"]:
            print("Sampling from freq:", frequency)
            # first choose target words based on the difficultly
            fp = f"resources/target_words/{LANGUAGE}/{frequency}_freq_100_{VERSION}"
            target_words = self.load_file(file_name=fp, file_ending=".txt").split('\n')
            if N_INSTANCES > 0:
                assert len(target_words) >= N_INSTANCES, \
                    f'Fewer words available ({len(target_words)}) than requested ({N_INSTANCES}).'
                target_words = random.sample(target_words, k=N_INSTANCES)

            # use the same target_words for the different player assignments
            experiment = self.add_experiment(f"{frequency}_{LANGUAGE}")
            experiment["max_turns"] = N_GUESSES

            describer_prompt = self.load_template("resources/initial_prompts/initial_describer")
            guesser_prompt = self.load_template("resources/initial_prompts/initial_guesser")
            experiment["describer_initial_prompt"] = describer_prompt
            experiment["guesser_initial_prompt"] = guesser_prompt

            for game_id in tqdm(range(len(target_words))):
                target = target_words[game_id]

                game_instance = self.add_game_instance(experiment, game_id)
                game_instance["target_word"] = target
                game_instance["related_word"] = []  # ps: add manually for now b.c. api doesn't provide ranking

                if len(game_instance["related_word"]) < N_RELATED_WORDS:
                    print(f"Found less than {N_RELATED_WORDS} related words for: {target}")


if __name__ == '__main__':
    TabooGameInstanceGenerator().generate()
