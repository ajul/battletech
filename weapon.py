import json
import os

data_path = (
    'C:/Program Files (x86)/Steam/steamapps/common/' +
    'BATTLETECH/BattleTech_Data/StreamingAssets/data'
    )

weapon_path = os.path.join(data_path, 'weapon')

def make_cost_string(data):
    cost = data['Description']['Cost'] // 1000
    if data['Description']['Purchasable']:
        return '<span style="color: white;">%d</span>' % cost
    else:
        return '<span style="color: gray;">%d</span>' % cost

def make_damage_string(data, key):
    damage_per_shot = data[key]
    shots = data['ShotsWhenFired']
    total_damage = damage_per_shot * shots

    hidden = '<span style="display: none;">%04d</span>' % total_damage
    shown = '%d' % total_damage
    if shots > 1:
        shown += ' (%d × %d)' % (damage_per_shot, shots)
    return hidden + shown

def make_range_string(data):
    hidden = '<span style="display: none;">%04d</span>' % data['MaxRange']
    shown = '%d / %d / %d' % (data['MinRange'], data['RangeSplit'][1], data['MaxRange'],)

    return hidden + shown

def make_other_string(data):
    other = []

    if data['IndirectFireCapable']:
        other.append('Indirect fire')
    
    if data['HeatDamage'] != 0:
        other.append('%d heat damage' % data['HeatDamage'])

    if len(data['statusEffects']) > 0:
        other.append('Inflicts +1 accuracy debuff')
    
    if data['RefireModifier']:
        other.append('%d refire accuracy' % data['RefireModifier'])

    if data['AccuracyModifier'] != 0:
        other.append('%+d accuracy' % data['AccuracyModifier'])
        
    if data['CriticalChanceMultiplier'] != 1.0:
        percent = (data['CriticalChanceMultiplier'] - 1.0) * 100.0
        other.append('%+d%% critical' % percent)

    return '<br/>'.join(other)

def make_row(data):
    row = [
        data['Description']['Name'].replace('+ ', '+'),
        data['Description']['Manufacturer'],
        data['Category'].replace('AntiPersonnel', 'Support'),
        make_cost_string(data),
        data['Tonnage'],
        data['InventorySize'],
        make_damage_string(data, 'Damage'),
        make_damage_string(data, 'Instability'),
        data['HeatGenerated'],
        make_range_string(data),
        make_other_string(data),
    ]

    return row

result = '{|class = "wikitable sortable"\n'
result += '! '

headers = [
    'Weapon',
    'Manufacturer',
    'Category',
    'Cost (k)',
    'Tonnage',
    'Slots',
    'Damage',
    'Stability<br/>damage',
    'Heat',
    'Range (m)<br/>min/opt/max',
    'Other',
    ]

result += ' !! '.join(headers)

result += '\n'

rows = []

for filename in os.listdir(weapon_path):
    if filename == 'WeaponTemplate.json': continue
    path = os.path.join(weapon_path, filename)
    f = open(path)
    data = json.load(f)
    f.close()
    
    if data['Category'] == "Melee": continue
    if data['WeaponSubType'] == 'AIImaginary': continue
    
    rows.append((data, make_row(data)))

def sort_func(data):
    name = data['Description']['Name']

    if 'AC/' in name:
        magic = ('AC', data['Tonnage'])
    elif 'Laser' in name or 'Pulse' in name:
        magic = ('Laser', data['Tonnage'])
    elif 'PPC' in name:
        magic = ('PPC', data['HeatGenerated'])
    elif 'RM' in name:
        magic = (name[:3], data['Tonnage'])
    else:
        magic = (name,)
        
    
    return (
        data['Category'].replace('AntiPersonnel', 'Support'),
        not data['Description']['Purchasable'],
        magic,
        data['Description']['Name'].replace('+ ', '+'),
        data['Description']['Manufacturer'],
        )

rows.sort(key = lambda x: sort_func(x[0]))

for _, row in rows:
    result += '|-\n'
    result += '| '
    result += ' || '.join(str(x) for x in row)
    result += '\n'

result += '|}\n'

print(result)
