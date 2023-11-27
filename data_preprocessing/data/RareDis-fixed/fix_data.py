import os
from tqdm import tqdm



def fix_data(data_path):
    data = {}
    for file in tqdm(os.listdir(data_path)):
        file_path = os.path.join(data_path, file)
        if os.path.isfile(file_path):
            if file_path.endswith('.ann'):
                new_lines = []
                # print(file_path)
                # data that cannot be repaired
                if 'Acute-Cholecystitis' in file_path:
                    new_file_path = file_path.replace('RareDis-v1', 'RareDis-fixed')
                    if os.path.exists(new_file_path):
                        os.remove(new_file_path)
                        os.remove(new_file_path.replace('.ann', '.txt'))
                    continue

                with open(file_path.replace('.ann', '.txt')) as f:
                    text = f.read()
                with open(file_path) as f:
                    # T5	RAREDISEASE 279 299	Abetalipoproteinemia
                    # R1	Anaphora Arg1:T1 Arg2:T2	
                    # R2	Anaphora Arg1:T3 Arg2:T4	
                    entity_ids = []
                    for line in f.readlines():
                        if line[0] == 'T':
                            line = line.strip()
                            entity_id, entity, name = line.split('\t')
                            entity_ids.append(entity_id)
                            if ';' in entity:
                                entity_type = entity.split()[0]
                                positions = entity.replace(';', ' ').replace(entity_type, '').strip().split()
                                num_positions = [int(p) for p in positions]
                                entity_start, entity_end = min(num_positions), max(num_positions)
                                name = text[entity_start:entity_end]
                                # check unclosed parenthesis
                                open_count = name.count('(')
                                close_count = name.count(')')
                                if open_count > close_count:
                                    name += ')'
                                    entity_end += 1
                                entity_start, entity_end = str(entity_start), str(entity_end)

                            else:
                                entity_type, entity_start, entity_end = entity.split()
                            new_line = entity_id + '\t' + entity_type + ' ' + entity_start + ' ' + entity_end + '\t' + name
                            new_lines.append(new_line)
                        elif line[0] == 'R':
                            line = line.strip()

                            relation_id, triple = line.split('\t')
                            relation_type, subject, object = triple.split()
                            subject = subject.split(':')[1]
                            object = object.split(':')[1]

                            if subject not in entity_ids:
                                continue
                            if object not in entity_ids:
                                if int(object.replace('T', '')) >= 40 and object[-1] == '0':
                                    object = object[:-1]
                                else:
                                    continue
                            new_line = relation_id + '\t' + relation_type + ' Arg1:' + subject + ' Arg2:' + object
                            new_lines.append(new_line)

                with open(file_path.replace('RareDis-v1', 'RareDis-fixed'), 'w') as f:
                    for line in new_lines:
                        f.write(line + '\n')


if __name__ == '__main__':

    train_data = fix_data('data/RareDis-v1/train')
    valid_data = fix_data('data/RareDis-v1/dev')
    test_data = fix_data('data/RareDis-v1/test')
