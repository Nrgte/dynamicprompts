from __future__ import annotations

import logging
import re

from dynamicprompts.commands import (
    Command,
    LiteralCommand,
    ReplaceCommand,
    SequenceCommand,
    VariantCommand,
    WildcardCommand,
)
from dynamicprompts.commands.variable_commands import (
    VariableAccessCommand,
    VariableAssignmentCommand,
)
from dynamicprompts.sampling_context import SamplingContext
from dynamicprompts.types import StringGen
from dynamicprompts.utils import rotate_and_join

logger = logging.getLogger(__name__)


class Sampler:
    def generator_from_command(
        self,
        command: Command,
        context: SamplingContext,
    ) -> StringGen:
        # This is purposely not a dict lookup/getattr magic thing, to make
        # it easier for code completion etc. to see what's going on.
        if isinstance(command, LiteralCommand):
            return self._get_literal(command, context)
        if isinstance(command, ReplaceCommand):
            return self._get_replace(command, context)
        if isinstance(command, SequenceCommand):
            return self._get_sequence(command, context)
        if isinstance(command, VariantCommand):
            return self._get_variant(command, context)
        if isinstance(command, WildcardCommand):
            return self._get_wildcard(command, context)
        if isinstance(command, VariableAssignmentCommand):
            raise NotImplementedError(
                "VariableAssignmentCommand should never be sampled",
            )
        if isinstance(command, VariableAccessCommand):
            return self._get_variable(command, context)
        return self._unsupported_command(command)

    def _unsupported_command(self, command: Command) -> StringGen:
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support {command.__class__.__name__}",
        )

    def _get_wildcard(
        self,
        command: WildcardCommand,
        context: SamplingContext,
    ) -> StringGen:
        return self._unsupported_command(command)

    def _get_variant(
        self,
        command: VariantCommand,
        context: SamplingContext,
    ) -> StringGen:
        return self._unsupported_command(command)

    def _get_sequence(
        self,
        command: SequenceCommand,
        context: SamplingContext,
    ) -> StringGen:
        # print (f"Sequence Command = {command}")
        tokens, context = context.process_variable_assignments(command.tokens)
        # print (f"tokens = {tokens}")
        sub_generators = []
        # sub_generators = [context.generator_from_command(c) for c in tokens]        
        for token in tokens:
            gen = context.generator_from_command(token)
            # print (f"gen = {gen} = {next(gen)}")
            sub_generators.append(next(gen))
        

        while True:
            yield command.separator.join(sub_generators)
            #strings = rotate_and_join(sub_generators, separator=command.separator)

    def _get_literal(
        self,
        command: LiteralCommand,
        context: SamplingContext,
    ) -> StringGen:
        while True:
            yield command.literal

    def _get_variable(
        self,
        command: VariableAccessCommand,
        context: SamplingContext,
    ) -> StringGen:
        variable = command.name
        command_to_sample = context.variables.get(variable, command.default)
        if not command_to_sample:
            if context.unknown_variable_value is None:
                raise KeyError(f"Variable {variable} is not defined in this context")
            elif isinstance(context.unknown_variable_value, str):
                command_to_sample = LiteralCommand(context.unknown_variable_value)
            else:
                command_to_sample = context.unknown_variable_value
        return context.for_sampling_variable(variable).generator_from_command(
            command_to_sample,
        )

    def _get_replace(
        self,
        command: ReplaceCommand,
        context: SamplingContext,
    ) -> StringGen:

        variable_name = ""
        if isinstance(command.var, VariableAccessCommand):
            variable_name = command.var.name

        var = next(context.generator_from_command(command.var))
        src = next(context.generator_from_command(command.src))
        dest = next(context.generator_from_command(command.dest))

        #var = var.replace(src, dest)
        var = re.sub(src, dest, var, 1)
        
        if (variable_name != ""):
            # var = "${" + variable_name + "=!" + var.strip() + "}"
            var_command = LiteralCommand(var.strip())
            context.set_variable(
                v_name = variable_name,
                command = var_command
            )

        while True:
            yield ""

