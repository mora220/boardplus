"""Board timer: one minute, 90 seconds, two minutes, 150 seconds, three minutes (no 5, 10 and 15 minutes)."""


def apply(s, rep, target):
    s = rep(s, "${[1, 2, 3, 5, 10, 15].map(m => `<button class=\"btn\" data-m=\"${m}\">${m} د</button>`).join('')}",
            "${[[60, 'دقيقة'], [90, '90 ثانية'], [120, 'دقيقتان'], [150, '150 ثانية'], [180, '3 دقائق']].map(([sc, n]) => `<button class=\"btn\" data-m=\"${sc / 60}\">${n}</button>`).join('')}")
    s = rep(s, '"مؤقت للحل":', '"دقيقة": "1 minute", "90 ثانية": "90 seconds", "دقيقتان": "2 minutes", "150 ثانية": "150 seconds", "3 دقائق": "3 minutes", "مؤقت للحل":') if '"مؤقت للحل":' in s else s
    return s
