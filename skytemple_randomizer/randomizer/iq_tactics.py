#  Copyright 2020-2021 Capypara and the SkyTemple Contributors
#
#  This file is part of SkyTemple.
#
#  SkyTemple is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SkyTemple is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SkyTemple.  If not, see <https://www.gnu.org/licenses/>.
from random import choice, randrange

from skytemple_files.common.util import get_binary_from_rom_ppmdu, set_binary_in_rom_ppmdu
from skytemple_files.hardcoded.iq import HardcodedIq, IqGroupsSkills
from skytemple_files.hardcoded.tactics import HardcodedTactics
from skytemple_files.patch.patches import Patcher
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.status import Status


class IqTacticsRandomizer(AbstractRandomizer):
    def step_count(self) -> int:
        i = 0
        if self.config['iq']['randomize_tactics']:
            i += 1
        if self.config['iq']['randomize_iq_gain']:
            i += 1
        if self.config['iq']['randomize_iq_groups']:
            i += 1
        if self.config['iq']['randomize_iq_skills']:
            i += 1
        return i

    def run(self, status: Status):
        ov10 = get_binary_from_rom_ppmdu(self.rom, self.static_data.binaries['overlay/overlay_0010.bin'])
        ov29 = get_binary_from_rom_ppmdu(self.rom, self.static_data.binaries['overlay/overlay_0029.bin'])
        patcher = Patcher(self.rom, self.static_data)
        additional_types_patch_applied = patcher.is_applied('AddTypes')
        if self.config['iq']['randomize_iq_groups']:
            if not patcher.is_applied('CompressIQData'):
                patcher.apply('CompressIQData')
        arm9 = bytearray(get_binary_from_rom_ppmdu(self.rom, self.static_data.binaries['arm9.bin']))

        if self.config['iq']['randomize_tactics']:
            status.step('Randomizing tactics...')
            tactics = HardcodedTactics.get_unlock_levels(arm9, self.static_data)

            minus_one_added = False
            new_tactics = []
            for tactic in tactics:
                if tactic == 999:
                    new_tactics.append(tactic)
                else:
                    if choice([True] + [False] * 12):
                        new_tactics.append(-1)
                        minus_one_added = True
                    else:
                        new_tactics.append(randrange(6, 51))

            while not minus_one_added:
                idx = randrange(0, len(new_tactics))
                if new_tactics[idx] != 999:
                    new_tactics[idx] = -1
                    minus_one_added = True

            HardcodedTactics.set_unlock_levels(new_tactics, arm9, self.static_data)

        if self.config['iq']['randomize_iq_gain']:
            status.step('Randomizing IQ gain...')
            iq_gains = HardcodedIq.get_gummi_iq_gains(arm9, self.static_data, additional_types_patch_applied)
            belly_gains = HardcodedIq.get_gummi_belly_heal(arm9, self.static_data, additional_types_patch_applied)

            new_iq_gains = []
            for l in iq_gains:
                li = []
                new_iq_gains.append(li)
                for e in l:
                    li.append(randrange(1, 6))

            new_belly_gains = []
            for l in belly_gains:
                li = []
                new_belly_gains.append(li)
                for e in l:
                    li.append(randrange(10, 40))

            HardcodedIq.set_gummi_iq_gains(new_iq_gains, arm9, self.static_data, additional_types_patch_applied)
            HardcodedIq.set_gummi_belly_heal(new_belly_gains, arm9, self.static_data, additional_types_patch_applied)
            HardcodedIq.set_wonder_gummi_gain(randrange(5, 20), arm9, self.static_data)
            HardcodedIq.set_nectar_gain(randrange(5, 20), ov29, self.static_data)
            HardcodedIq.set_juice_bar_nectar_gain(randrange(5, 20), arm9, self.static_data)

        if self.config['iq']['randomize_iq_groups']:
            status.step('Randomizing IQ groups...')
            if not patcher.is_applied('CompressIQData'):
                patcher.apply('CompressIQData')
            iq_groups = IqGroupsSkills.read_compressed(arm9, self.static_data)

            iq_skills = HardcodedIq.get_iq_skills(arm9, self.static_data)

            new_iq_groups = []
            for _ in iq_groups:
                li = []
                new_iq_groups.append(li)
                for idx in range(len(iq_skills)):
                    if idx == 22 or choice([True, False]):
                        li.append(idx)

            IqGroupsSkills.write_compressed(arm9, new_iq_groups, self.static_data)

        if self.config['iq']['randomize_iq_skills']:
            status.step('Randomizing IQ skills...')
            iq_skills = HardcodedIq.get_iq_skills(arm9, self.static_data)

            for skill_idx, skill in enumerate(iq_skills):
                if skill.iq_required != 9999:
                    if skill_idx == 22 or choice([True] + [False] * 12):
                        skill.iq_required = -1
                    else:
                        skill.iq_required = randrange(1, 900)

            HardcodedIq.set_iq_skills(iq_skills, arm9, self.static_data)

        set_binary_in_rom_ppmdu(self.rom, self.static_data.binaries['arm9.bin'], arm9)
        set_binary_in_rom_ppmdu(self.rom, self.static_data.binaries['overlay/overlay_0010.bin'], ov10)
        set_binary_in_rom_ppmdu(self.rom, self.static_data.binaries['overlay/overlay_0029.bin'], ov29)
        status.done()
