import tempfile
from subprocess import call
from os import path

class MateToolsLemmazizer():
    def __init__(self, transition='./mate_tools/transition-1.30.jar', model='./mate_tools/models/lemma-ger-3.6.model'):
        self.transition = transition
        self.model = model
    
    def lemmatize(self, tokens):
        with tempfile.NamedTemporaryFile(mode='w+') as in_f:
            in_f.write(self.as_conll_09_str(tokens))
            in_f.flush()
            with tempfile.NamedTemporaryFile() as out_f:
                project_path = path.dirname(path.realpath(__file__))
                print(project_path)
                call(f"java -Xmx2G -classpath {project_path}/mate_tools/transition-1.30.jar is2.lemmatizer2.Lemmatizer -model {project_path}/mate_tools/models/lemma-ger-3.6.model -test {in_f.name} -out {out_f.name} -uc", shell=True)
                out = out_f.read().decode()
        return self.parse_conll_09_str(out)
            
    def as_conll_09_str(self, tokens):
        conll_09_str = ""
        for i, token in enumerate(tokens):
            conll_09_str += f"{i}\t{token}\n"
        return conll_09_str
    
    def parse_conll_09_str(self, string):
        lines = string.split('\n')
        tokens = []
        for line in lines:
            print(line)
            cells = line.split('\t')
            if len(cells) > 1:
                tokens.append(cells[3])
        return tokens
