def permute(stops):
    if len(stops) == 1:
        print('BASE CASE:')
        print(stops)
        if 'start' in stops[0].keys():
            result = [{'dest': stops[0]['start']}, {'dest': stops[0]['end']}]
            return [result]
        return [stops]
    permutations = []
    for i in range(len(stops)):
        first = stops[i]
        remaining = stops[:i] + stops[i+1:]
        if 'start' in first.keys():
            remaining.append({'dest': first['end']})
            first = {'dest': first['start']}
    permuted = permute(remaining)
    for p in permuted:
        permutations.append([first] + p)
    return permutations


data = [{'start': [2, 4], 'end': [6, 8]}, {'start': [1, 3], 'end': [5, 7]}]
data = list(data)
permutations = permute(data)
print('final results:')
for p in permutations:
    print(p)