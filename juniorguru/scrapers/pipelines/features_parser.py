import itertools
import re


LANG_MAPPING = {
    'en': 'ENGLISH_REQUIRED',
    'cs': 'CZECH_REQUIRED',
    'sk': 'SLOVAK_REQUIRED',
}

# [\b\W] is necessary because if the first thing ends with \W (e.g. period),
# the subseqent character doesn't qualify as a word boundary, also words
# followed by e.g. / wouldn't match
FOLLOWED_BY_PATTERN = r'[\b\W](.+[\b\W])?'


def rule(identifier, *patterns, ignorecase=True, any_order=False):
    compile_flags = re.IGNORECASE if ignorecase else 0
    pattern_lists = [([pattern] if isinstance(pattern, str) else list(pattern))
                     for pattern in patterns]
    if any_order:
        permutations = itertools.permutations(pattern_lists)
    else:
        permutations = [pattern_lists]
    for pattern_lists in permutations:
        for patterns_tuple in itertools.product(*pattern_lists):
            pattern = FOLLOWED_BY_PATTERN.join(patterns_tuple)
            rule_re = re.compile(''.join([
                # implicit boundary if not ^
                '' if pattern[0] == '^' else r'\b',
                # pattern itself
                pattern,
                # implicit boundary if not $
                '' if pattern[-1] == '$' else r'\b',
            ]), compile_flags)
            yield (identifier, rule_re)


def rules(rules):
    return list(itertools.chain.from_iterable(rules))


TECH_DEGREES_EN = [r'ph\.?d\.?', r'm\.?sc?\.?', r'b\.?sc?\.?',
                   r'bachelor[^ ]*s?', r'master[^ ]*s']
TECH_DEGREE_FIELDS_EN = [r'computer science', r'informatics',
                         r'software', r'technical', r'engineering', r'computing']
ADVANCED_SKILLS_ADJECTIVES_EN = [r'excellent', r'professional', r'strong',
                                 r'very good', r'thorough', r'solid', r'sound',
                                 r'significant', r'deep(er)?', r'extensive',
                                 r'superior', r'advanced', r'profound',
                                 r'detailed', r'notable', r'extended']
SKILLS_NOUNS_EN = [r'skills', r'abilities', r'capabilities', r'knowledge',
                   r'experience', r'background', r'understanding', r'expertise',
                   r'know.?how', r'familiarity']
LANGUAGE_KEYWORDS_EN = [r'language', r'knowledge', r'speak\w+', r'skills?',
                        r'native', r'command of', r'spoken', r'proficie\w+',
                        r'fluen\w+', r'communication']


RULES_EN = rules([
    rule('TECH_DEGREE_REQUIRED', TECH_DEGREES_EN + [r'degree', r'studies'], TECH_DEGREE_FIELDS_EN),
    rule('TECH_DEGREE_REQUIRED', r'completed', r'education', TECH_DEGREE_FIELDS_EN),
    rule('TECH_DEGREE_REQUIRED', TECH_DEGREE_FIELDS_EN, [r'degree', r'education', r'university']),
    rule('TECH_DEGREE_REQUIRED', TECH_DEGREES_EN + [r'university'], [r'degree']),
    rule('TECH_DEGREE_REQUIRED', r'academic record'),
    rule('YEARS_EXPERIENCE_REQUIRED', r'[\d\-\+ ]+[^\d]+years?.?', r'(experience|track record)'),
    rule('YEARS_EXPERIENCE_REQUIRED', r'experience\b.*[\d\-\+ ]+[^\d]+years?.?'),
    rule('YEARS_EXPERIENCE_REQUIRED', r'[\d\+] experience'),
    rule('YEARS_EXPERIENCE_REQUIRED', r'min(\.|imum) [\d\+] years?'),
    rule('YEARS_EXPERIENCE_REQUIRED', [r'multi(ple)?', r'several'], r'years?', r'experience'),
    rule('ADVANCED_REQUIRED', ADVANCED_SKILLS_ADJECTIVES_EN, SKILLS_NOUNS_EN),
    rule('ADVANCED_REQUIRED', r'experience', r'within', [r'professional', r'commercial'], r'setting'),
    rule('ADVANCED_REQUIRED', r'experience', [r'architect\w+', r'building', r'consuming', r'deploy\w+']),
    rule('ADVANCED_REQUIRED', [r'commercial', r'solid', r'previous', r'implementation', r'hands-on', r'architect\w+'], [r'experience', r'knowledge']),
    rule('ADVANCED_REQUIRED', r'work(ing)? (experience|knowledge)'),
    rule('ADVANCED_REQUIRED', r'(proficien(cy|t)|fluen(cy|t)|well.?versed) (in|with|\w+ing)'),
    rule('ADVANCED_REQUIRED', r'responsibility', r'for', r'(architecture|design)'),
    rule('ADVANCED_REQUIRED', r'experience', r'everything else'),
    rule('ADVANCED_REQUIRED', SKILLS_NOUNS_EN, r'vari(ety|ous)'),
    rule('ADVANCED_REQUIRED', r'experienced?', r'as', r'(engineer|developer)'),
    rule('ADVANCED_REQUIRED', r'you', r'(consider yourself|are)', r'(expert|researcher|hacker)'),
    rule('ADVANCED_REQUIRED', r'self-starter'),
    rule('ADVANCED_REQUIRED', r'(intermediate|medior)'),
    rule('ADVANCED_REQUIRED', r'take', r'(ownership|responsibility) (on|of|for)'),
    rule('ADVANCED_REQUIRED', r'manage', r'priorities'),
    rule('ADVANCED_REQUIRED', r'translate', r'business'),
    rule('ADVANCED_REQUIRED', r'analysis', r'experience'),
    rule('ADVANCED_REQUIRED', r'have', r'superpowers?'),
    rule('ADVANCED_REQUIRED', r'must have', r'experience'),
    rule('ADVANCED_REQUIRED', r'previous experience with'),
    rule('ADVANCED_REQUIRED', r'(provable|relevant)', r'industry experience'),
    rule('LEADERSHIP_REQUIRED', r'(leadership|mentoring) (experience|skills)'),
    rule('LEADERSHIP_REQUIRED', r'experience', r'(leading|leader)'),
    rule('LEADERSHIP_REQUIRED', r'lead(ing)?', r'(teams?|courses?)'),
    rule('LEADERSHIP_REQUIRED', r'lead(ing)?', r'by example'),
    rule('LEADERSHIP_REQUIRED', r'delegat\w+', r'others'),
    rule('LEADERSHIP_REQUIRED', r'mentor(ing)?', r'junio\w+'),
    rule('INDEPENDENCE_PREFERRED', r'(execute|work(ing)?|operat(e|ing)|solv(e|ing))', r'(independen\w+|autonomou\w+)'),
    rule('INDEPENDENCE_PREFERRED', r'(independent|autonomous)', r'working'),
    rule('INDEPENDENCE_PREFERRED', r'(little|minimal|minimum)', r'supervision'),
    rule('INDEPENDENCE_PREFERRED', r'self.?sufficient'),
    rule('EXPLICITLY_SENIOR', r'senior'),
    rule('EXPLICITLY_SENIOR', [r'seasoned', r'experienced', r'practiced', r'specialist'], [r'engineer', r'developer']),
    rule('EXPLICITLY_JUNIOR', [r'junior', r'padawan', r'internship', r'intern', r'trainee']),
    rule('EXPLICITLY_JUNIOR', r'students welcome'),
    rule('JUNIOR_FRIENDLY', r'do(es)?(n.?t| not) matter'),
    rule('JUNIOR_FRIENDLY', r'entry.?level'),
    rule('JUNIOR_FRIENDLY', r'learn a (lot|ton)'),
    rule('JUNIOR_FRIENDLY', r'whether', r'you', r'know', r'or', r'not(hing)?'),
    rule('JUNIOR_FRIENDLY', r'you', r'missing'),
    rule('JUNIOR_FRIENDLY', r'start', r'career'),
    rule('JUNIOR_FRIENDLY', r'school', r'projects?'),
    rule('JUNIOR_FRIENDLY', r'(under|with)', r'guidance'),
    rule('JUNIOR_FRIENDLY', r'(guided|mentored) by', r'(engineer|developer)s?'),
    rule('JUNIOR_FRIENDLY', r'learn(ing)? by doing'),
    rule('JUNIOR_FRIENDLY', r'not?', r'necessar(y|ily)'),
    rule('JUNIOR_FRIENDLY', r'open', r'graduat\w+'),
    rule('JUNIOR_FRIENDLY', r'not?', r'big deal'),
    rule('JUNIOR_FRIENDLY', r'at least', r'(one|1)', r'programming language'),
    rule('JUNIOR_FRIENDLY', r'(educational|school)', r'experience'),
    rule('LEARNING_REQUIRED', r'will\w*', r'to', r'learn'),
    rule('CZECH_REQUIRED', r'czech', LANGUAGE_KEYWORDS_EN, any_order=True),
    rule('SLOVAK_REQUIRED', r'slovak', LANGUAGE_KEYWORDS_EN, any_order=True),
    rule('GERMAN_REQUIRED', r'german', LANGUAGE_KEYWORDS_EN, any_order=True),
])
SUPPRESSING_RULES_EN = rules([
    rule('', r'(is|are|would be|as)( an?)? ((big )?plus|benefit|advantage)'),
    rule('', r'we welcome'),
    rule('', r'nice to have'),
    rule('', r'an? advantage'),
    rule('', r'training'),
    rule('', r'if', r'interested'),
    rule('', r'send us'),
    rule('', r'apply'),
    rule('TECH_DEGREE_REQUIRED', r'or', r'equivalent', r'experience'),
    rule('ADVANCED_REQUIRED', r'communications? skills'),
    rule('ADVANCED_REQUIRED', r'present(ing|ations?) skills'),
    rule('ADVANCED_REQUIRED', r'english'),
    rule('ADVANCED_REQUIRED', r'depend(s|ing) on your'),
    rule('ADVANCED_REQUIRED', r'(ms|microsoft) office'),
    rule('ADVANCED_REQUIRED', r'windows', r'operat\w+ systems?'),
    rule('ADVANCED_REQUIRED', r'not?', r'necessary'),
    rule('ADVANCED_REQUIRED', r'(user|developer|customer) experience'),
    rule('ADVANCED_REQUIRED', r'(knowledge.?(base|sharing))'),
    rule('ADVANCED_REQUIRED', r'^\W*we'),
    rule('ADVANCED_REQUIRED', r'^\W*this'),
    rule('ADVANCED_REQUIRED', r'first'),
    rule('ADVANCED_REQUIRED', r'(professional|personal|technical) (requirements|skills|expertise)'),
    rule('ADVANCED_REQUIRED', r'(educational|school)', r'experience'),
    rule('ADVANCED_REQUIRED', r'at least', r'(one|1)', r'programming language'),
    rule('EXPLICITLY_SENIOR', r'(junior|jnr)'),
    rule('EXPLICITLY_SENIOR', [r'collaborate', r'work'], r'with', r'(engineer|developer)s?'),
    rule('EXPLICITLY_SENIOR', r'(guided|mentored|supported) by'),
    rule('EXPLICITLY_JUNIOR', r'(senior|mentor)'),
    rule('CZECH_REQUIRED', r'courses?'),
    rule('CZECH_REQUIRED', r'czech (is not|isn\.t|not) required'),
    rule('SLOVAK_REQUIRED', r'courses?'),
    rule('SLOVAK_REQUIRED', r'slovak (is not|isn\.t|not) required'),
    rule('GERMAN_REQUIRED', r'courses?'),
    rule('GERMAN_REQUIRED', r'german (is not|isn\.t|not) required'),
    rule('LEADERSHIP_REQUIRED', r'(industry|join)'),
    rule('INDEPENDENCE_PREFERRED', r'operate', r'independent'),
    rule('INDEPENDENCE_PREFERRED', [r'intelligence', r'software'], r'autonomous\w*', any_order=True),
])


ADVANCED_SKILLS_ADJECTIVES_CS = [r'pokro??il\w+', r'v??born\w+', r'skv??l\w+',
                                 r'komer??n??', r'dobr\w+', r'perfekt\w*',
                                 r'solidn\w*']
SKILLS_NOUNS_CS = [r'znalost\w*', r'zku??enost\w*', r'my??len??', r'background']
TECH_DEGREES_CS = [r'vysoko??kol\w+', r'v??', r'studi(um|a|i)', r'titul\w*',
                   r'absolven\w+']
TECH_DEGREE_FIELDS_CS = [r'techn\w+', r'informati\w+', r'it']


RULES_CS = rules([
    rule('JUNIOR_FRIENDLY', SKILLS_NOUNS_CS, r'programovac??\w*', r'jazyk\w*'),
    rule('LEADERSHIP_REQUIRED', SKILLS_NOUNS_CS, r'(veden??\w*|v??st)', r't??m\w*'),
    rule('TECH_DEGREE_REQUIRED', TECH_DEGREES_CS, TECH_DEGREE_FIELDS_CS, any_order=True),
    rule('ADVANCED_REQUIRED', ADVANCED_SKILLS_ADJECTIVES_CS, SKILLS_NOUNS_CS),
    rule('YEARS_EXPERIENCE_REQUIRED', r'(a(le)?spo??|minim\w+|min|\d+)[\W]*(rok|let|rok[y??u]|ro??n??|letou)'),
    rule('ENGLISH_REQUIRED', r'(angli??tin\w+|anglick\w+)'),
    rule('ENGLISH_REQUIRED', r'AJ', ignorecase=False),
    rule('ENGLISH_REQUIRED', r'EN', ignorecase=False),
    rule('GERMAN_REQUIRED', r'NJ', ignorecase=False),
    rule('GERMAN_REQUIRED', r'(n??m??in\w+|n??meck\w+)'),
    rule('ADVANCED_REQUIRED', r'zku??enos\w+', r'(v??v??je|v??voj)\w+'),
    rule('ADVANCED_REQUIRED', r'nejsi', r'zelen????'),
    rule('ADVANCED_REQUIRED', [r'rozhled(em)?', r'p??ehled(em)?', r'architekt\w*']),
    rule('ADVANCED_REQUIRED', r'prax\w+', [r've?', r'se?']),
    rule('ADVANCED_REQUIRED', r'm????', r'za sebou'),
    rule('ADVANCED_REQUIRED', r'z?odpov??dn\w+', r'za'),
    rule('ADVANCED_REQUIRED', r'samostatn\w+', r'??e??\w+', r'probl??m\w+'),
    rule('ADVANCED_REQUIRED', r'nasm??rovat', r'kolegy', any_order=True),
    rule('ADVANCED_REQUIRED', r'medior\w*'),
    rule('EXPLICITLY_SENIOR', r'senior\w*'),
    rule('EXPLICITLY_JUNIOR', [r'junior\w*', r'jnr', r'padawan\w*', r'u??e??', r'internship', r'st????\w*']),
    rule('INDEPENDENCE_PREFERRED', r'samostatn\w+|individu??ln\w+'),
    rule('JUNIOR_FRIENDLY', [r'[nz]au????(me|??)', r'zau??en??', r'p??e??kol??(me|??)', r'p??e??kolen??', r'p??eu????(me|??)', r'p??eu??en??', r'zacvi????(me|??)', r'z??cvik']),
    rule('JUNIOR_FRIENDLY', r'(prostor\w*|p????le??itost\w*|mo??nost\w*)', r'u??it'),
    rule('JUNIOR_FRIENDLY', r'(prostor\w*|p????le??itost\w*|mo??nost\w*)', r'z??sk\w+', r'(zku??en\w+|prax\w+)'),
    rule('JUNIOR_FRIENDLY', r'(absolvent\w*|studuje??|ze ??koly|??koln??)'),
    rule('JUNIOR_FRIENDLY', [r'vhodn\w+', r'nebr??n??me'], [r'student\w*', r'absolvent\w*']),
    rule('JUNIOR_FRIENDLY', r'a(le)?spo??', r'z??kladn??'),
    rule('JUNIOR_FRIENDLY', r'a(le)?spo??', [r'jeden', r'1'], r'projekt'),
    rule('JUNIOR_FRIENDLY', r'(nem[a??]\w*|nemus??\w*)', r'(zku??en\w*|um??t|prax\w+|za sebou)'),
    rule('JUNIOR_FRIENDLY', r'\w*start\w*', r'kari??r\w+'),
    rule('JUNIOR_FRIENDLY', [r'zlep??ov\w+', r'roz??i??ov\w+'], r'znalost\w+'),
    rule('JUNIOR_FRIENDLY', [r'spole??n??', r'spolupr[a??]c\w+'], r'se?', [r'senior\w+', r'mentor\w+']),
    rule('JUNIOR_FRIENDLY', r'dostane\w+', [r'senior\w+', r'mentor\w+']),
    rule('JUNIOR_FRIENDLY', r'k sob??', r'm??t', r'n??koho', r'pom????\w+', any_order=True),
    rule('JUNIOR_FRIENDLY', r'v z??dech', r't??m', r'zku??en\w*', any_order=True),
    rule('JUNIOR_FRIENDLY', r'mentor\w+', [r'ze strany', r'od'], [r'koleg??', r'zku??en\w+', r'senior\w+']),
    rule('JUNIOR_FRIENDLY', r'vezme(me)?', r'na starost', any_order=True),
    rule('JUNIOR_FRIENDLY', r'bude(me)?', r'pom??hat', any_order=True),
    rule('JUNIOR_FRIENDLY', r'pom????eme ti'),
    rule('JUNIOR_FRIENDLY', [r'pom????\w+', r'pomoc', r'pomohou'], [r'\w+u??it', r'\w+u??en\w+'], any_order=True),
    rule('JUNIOR_FRIENDLY', [r'pom????\w+', r'pomoc', r'pomohou'], r'r??di', any_order=True),
    rule('JUNIOR_FRIENDLY', r'mo??n\w+ \w+u??(it|????|??te)'),
    rule('JUNIOR_FRIENDLY', r'nebo', r'\w+u??(it|????|??te|??me)'),
    rule('JUNIOR_FRIENDLY', [r'nevad??', r'nez??le????']),
    rule('LEARNING_REQUIRED', r'(chce\w*|cht??j\w*|cht??t|chu??|ochot\w+|schopn\w+)', r'(u??it|na sob??|rozv??j\w+)'),
    rule('LEARNING_REQUIRED', r'u??it se'),
    rule('LEARNING_REQUIRED', [r'u??en??', r'rozv\w+'], r'sebe sam\w+'),
    rule('LEARNING_REQUIRED', r'rozv\w+', r'se v'),
])
SUPPRESSING_RULES_CS = rules([
    rule('', r'v??hodou'),
    rule('', [r'po??l\w+', r'??ivotopis\w*']),
    rule('YEARS_EXPERIENCE_REQUIRED', [r'stabiln??', r'rodinn??'], r'firma'),
    rule('YEARS_EXPERIENCE_REQUIRED', r'trhu'),
    rule('YEARS_EXPERIENCE_REQUIRED', r'u?? \d+'),
    rule('YEARS_EXPERIENCE_REQUIRED', r'v??kov\w+', r'pr??m??r\w*'),
    rule('EXPLICITLY_SENIOR', r'(junior|jnr|juniorn??\w*)'),
    rule('EXPLICITLY_SENIOR', r'(spolu)?prac\w+ se?'),
    rule('EXPLICITLY_SENIOR', r'ud??l??me', r'z (tebe|v??s)'),
    rule('EXPLICITLY_SENIOR', r'koleg\w+'),
    rule('EXPLICITLY_SENIOR', [r'spole??n??', r'spolupr[a??]c\w+', r't??m\w*', r'tandem\w*'], r'se?', r'senior\w*'),
    rule('EXPLICITLY_JUNIOR', r'(seniorn??|senior)'),
    rule('EXPLICITLY_JUNIOR', r'(spolu)?prac\w+ se?'),
    rule('EXPLICITLY_JUNIOR', r'hled??(??|te)'),
    rule('ENGLISH_REQUIRED', r'(v??uk\w|kurz\w*)'),
    rule('ENGLISH_REQUIRED', r'[Bb][Ee][Zz] (AJ|EN)', ignorecase=False),
    rule('ENGLISH_REQUIRED', r'u?v??t??(me|n\w+)'),
    rule('GERMAN_REQUIRED', r'(v??uk\w|kurz\w*)'),
    rule('GERMAN_REQUIRED', r'u?v??t??(me|n\w+)'),
    rule('ADVANCED_REQUIRED', r'nen??', [r'nutn\w+', r'pot??eb\w+']),
    rule('ADVANCED_REQUIRED', r'nez??le????'),
    rule('ADVANCED_REQUIRED', r'??kol\w+'),
    rule('ADVANCED_REQUIRED', r'z??sk\w+', r'(rozhled|p??ehled|prax)\w*'),
    rule('ADVANCED_REQUIRED', [r'jsme', r't??m\w*'], r'z?odpov??dn\w+'),
    rule('ADVANCED_REQUIRED', r'(chce\w*|cht??j\w*|cht??t)'),
    rule('ADVANCED_REQUIRED', [r'??J', r'SJ', r'AJ'], ignorecase=False),
    rule('ADVANCED_REQUIRED', r'[Pp]rax\w+ v IT', ignorecase=False),
    rule('ADVANCED_REQUIRED', [r'angli??tin\w+', r'anglick\w+', r'n??m??in\w+', r'n??meck\w+', r'??e??tin\w+', r'sloven??tin\w+']),
    rule('ADVANCED_REQUIRED', r'(spolu)?prac\w+ se?', r'architekt\w*'),
    rule('ADVANCED_REQUIRED', r'pod??lej(te)? se', r'architekt\w*'),
    rule('ADVANCED_REQUIRED', r'spole??n??', r'se?', r'architekt\w*'),
    rule('ADVANCED_REQUIRED', r'u?v??t??(me|n\w+)'),
    rule('TECH_DEGREE_REQUIRED', r'(??i|nebo)', r'prax\w+'),
    rule('TECH_DEGREE_REQUIRED', r'nerozhoduje'),
    rule('TECH_DEGREE_REQUIRED', r'u?v??t??(me|n\w+)'),
    rule('INDEPENDENCE_PREFERRED', [r'mzd\w+', r'plat', r'plato\w+']),
    rule('INDEPENDENCE_PREFERRED', [r'HPP', r'I??', r'I??O'], ignorecase=False),
    rule('INDEPENDENCE_PREFERRED', r'??ivnost\w*'),
    rule('INDEPENDENCE_PREFERRED', [r'(mi[ck]ro)\.?servi[cs]\w+']),
    rule('JUNIOR_FRIENDLY', [r'??J', r'SJ', r'AJ'], ignorecase=False),
    rule('JUNIOR_FRIENDLY', r'home[\.\s]?office'),
    rule('JUNIOR_FRIENDLY', [r'angli??tin\w+', r'anglick\w+', r'n??m??in\w+', r'n??meck\w+', r'??e??tin\w+', r'sloven??tin\w+']),
])


RULES = {'en': RULES_EN, 'cs': RULES_CS}
SUPPRESSING_RULES = {'en': SUPPRESSING_RULES_EN, 'cs': SUPPRESSING_RULES_CS}


class Pipeline():
    def process_item(self, item, spider):
        parse_results = deduplicate(itertools.chain(
            parse_from_sentence(item['title'], item['lang']),
            parse_from_sentences(item['description_sentences'], item['lang']),
        ))
        item['features'] = [
            dict(name=LANG_MAPPING[item['lang']],
                 origin='language_filter')
        ] + [
            dict(name=rule_id,
                 origin='features_parser',
                 sentence=sentence,
                 patterns=patterns)
            for rule_id, sentence, patterns in parse_results
        ]
        return item


def deduplicate(parse_results):
    seen = {}
    for rule_id, sentence, pattern in parse_results:
        key = (rule_id, sentence)
        seen.setdefault(key, [])
        seen[key].append(pattern)
    return [(rule_id, sentence, patterns) for (rule_id, sentence), patterns
            in seen.items()]


def parse_from_sentences(sentences, lang):
    return itertools.chain.from_iterable(parse_from_sentence(sentence, lang)
                                         for sentence in sentences)


def parse_from_sentence(sentence, lang):
    for rule_id, rule_re in RULES[lang]:
        match = rule_re.search(sentence)
        if (match and
            not is_supressed(rule_id, sentence, lang)):
            yield (rule_id, sentence, rule_re.pattern)


def is_supressed(rule_id, sentence, lang):
    for suppressing_rule_id, suppressing_rule_re in SUPPRESSING_RULES[lang]:
        is_relevant = (suppressing_rule_id == '' or
                       suppressing_rule_id == rule_id)
        if is_relevant and suppressing_rule_re.search(sentence):
            return True
    return False
