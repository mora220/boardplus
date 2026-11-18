"""Quiz: a question ends early only when every student of the session has answered, online or not; while anyone
has not answered, the time runs to the end."""


def apply(s, rep, target):
    a = "    const N = onlineCount(); if (" + ("QZ.auto && " if target == 'rb' else "") + "r.phase === 'q' && !r.paused && N && Object.keys(QZ.answers).length >= N)"
    return rep(s, a, a.replace("const N = onlineCount();", "const N = [...T.st.values()].filter(x => x && x.info && x.info.name).length;"))
