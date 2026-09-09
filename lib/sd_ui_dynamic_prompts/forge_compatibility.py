import torch
from modules import prompt_parser

def apply_forge_patch():
    """
    Patches modules.prompt_parser.stack_conds to handle variable-length tensors.
    This fixes the 'RuntimeError: stack expects each tensor to be equal size'
    error when prompts of different tokenized lengths (e.g. dynamic or LLM
    prompts) produce conditioning tensors with varying sequence lengths in a
    batch. Padding is dimension-agnostic (2D or 3D tensors).
    """
    
    def improved_stack_conds(tensors):
        if not tensors:
            return torch.tensor([])

        try:
            return torch.stack(tensors)
        except Exception:
            # Prompts with different tokenized lengths (e.g. dynamic/LLM prompts)
            # produce tensors of different shapes that cannot be stacked directly.
            # Pad the shorter tensors by repeating their last vector along dim 0
            # so that all tensors share the same shape. Works for any tensor
            # dimensionality (2D [seq, hidden] or 3D [seq, channels, hidden]).

            token_count = max([x.shape[0] for x in tensors])
            new_tensors = []

            for x in tensors:
                if x.shape[0] == token_count:
                    new_tensors.append(x)
                else:
                    diff = token_count - x.shape[0]
                    last_vector = x[-1:]
                    repeats = [diff] + [1] * (x.dim() - 1)
                    last_vector_repeated = last_vector.repeat(repeats)
                    new_tensors.append(torch.cat([x, last_vector_repeated], dim=0))

            return torch.stack(new_tensors)

    # Apply the patch
    prompt_parser.stack_conds = improved_stack_conds
