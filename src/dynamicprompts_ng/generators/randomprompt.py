from __future__ import annotations

import dataclasses
import logging
from random import Random

from dynamicprompts.commands.base import SamplingMethod
from dynamicprompts.constants import DEFAULT_RANDOM
from dynamicprompts.generators.promptgenerator import PromptGenerator
from dynamicprompts.parser.config import ParserConfig, default_parser_config
from dynamicprompts.sampling_context import SamplingContext
from dynamicprompts.wildcards import WildcardManager

logger = logging.getLogger(__name__)

def _get_random(*, seed: int | None, unlink_seed_from_prompt: bool) -> Random:
    if unlink_seed_from_prompt:
        return DEFAULT_RANDOM
    rand = Random()
    if seed is not None:
        rand.seed(seed)
    return rand


# variables: dict[int, dict[str, Command]] = dataclasses.field(default_factory=dict)
variables: dict[int, dict[str, Command]] = {}

class RandomPromptGenerator(PromptGenerator):

    def __init__(
        self,
        wildcard_manager: WildcardManager | None = None,
        seed: int | None = None,
        unlink_seed_from_prompt: bool = False,
        ignore_whitespace: bool = False,
        parser_config: ParserConfig = default_parser_config,
        #instance_variables: dict[int, dict[str, Command]] = None,
    ) -> None:
        global variables
        self.instance_variables = variables

        wildcard_manager = wildcard_manager or WildcardManager()
        self._context = SamplingContext(
            wildcard_manager=wildcard_manager,
            default_sampling_method=SamplingMethod.RANDOM,
            ignore_whitespace=ignore_whitespace,
            parser_config=parser_config,
            rand=_get_random(
                seed=seed,
                unlink_seed_from_prompt=unlink_seed_from_prompt,
            ),
        )

    def generate(
        self,
        template: str | None = None,
        num_images: int = 1,
        *,
        seeds: list[int] | int | None = None,
        **kwargs,
    ) -> list[str]:
        if not template:
            template = ""

        if seeds:
            if isinstance(seeds, int):
                seeds = [seeds]

            if len(seeds) == 1:
                seeds = seeds * num_images

            if len(seeds) != num_images:
                raise ValueError(f"Expected {num_images} seeds, but got {len(seeds)}")

            # gen = self._context.sample_prompts(template, num_images)
            # print (f"Seeds is set to: {seeds}")
            # print (f"The ID of variables is : {id(variables)}")
            # print (f"The ID of instance variables is : {id(self.instance_variables)}")

            all_in_dict = True
            for index, seed in enumerate(seeds):
                if not seed in self.instance_variables:
                    all_in_dict = False

            if not all_in_dict:
                # print (f"Resetting variables.")
                self.instance_variables.clear()

            # print (f"Variable count = {len(variables)}")       
            # print (f"template = {template}")
            num_images = 1

            prompts = []
            # for seed in seeds:
            for index, seed in enumerate(seeds):
                if seed in self.instance_variables:
                    self._context.set_variables(self.instance_variables[seed])
                # context.rand.seed(seed)
                gen = self._context.sample_prompts(template, num_images)
                # self._context.rand.seed(seed)
                prompts.append(next(iter(gen)))

                # Populate variables
                if not seed in self.instance_variables:                    
                    self.instance_variables[seed] = self._context.get_variables().copy()
                else:
                    for key, value in self._context.get_variables().items():
                        self.instance_variables[seed][key] = value

                # if (index < len(seeds) - 1):
                # print(f"current variables = {variables[seed]}")
                self._context.reset_variables()

            return prompts
        else:
            return list(self._context.sample_prompts(template, num_images))
