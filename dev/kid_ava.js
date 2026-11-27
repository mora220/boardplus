/* BoardPlus kids: the student's monster buddies — original, hand-built SVG characters (no external art). */
const KID_AVA = (() => {
  const PAL = [
    ['#9a7bff', '#6c4ce6', '#d8ccff'], ['#45b8ff', '#1f8ee6', '#c6e9ff'], ['#33d6a6', '#14a77c', '#c4f4e5'],
    ['#ffc940', '#e59f12', '#fff0b8'], ['#ff7f7f', '#e05252', '#ffd6d6'], ['#ff82cb', '#de52a3', '#ffd7ef'],
    ['#ff9e47', '#e3761a', '#ffe0c2'], ['#a2df45', '#72b51c', '#e4f7c4'], ['#2cc8cc', '#11999e', '#c0f0f1'],
    ['#6584ff', '#3c5ce0', '#d0daff'], ['#cd72ff', '#a24bdb', '#f0d8ff'], ['#ff6276', '#d93a52', '#ffcfd6']
  ];
  //          shape top     eyes mouth  extra
  const SET = [
    ['blob', 'horns', 2, 'grin', 'belly'], ['egg', 'antenna', 1, 'smile', 'spots'], ['ghost', 'tuft', 2, 'o', 'belly'],
    ['box', 'ears', 2, 'fang', 'spots'], ['blob', 'uni', 2, 'smile', 'belly'], ['egg', 'horns', 3, 'grin', 'belly'],
    ['box', 'antenna', 2, 'grin', 'belly'], ['ghost', 'ears', 1, 'fang', 'spots'], ['blob', 'tuft', 2, 'fang', 'spots'],
    ['egg', 'ears', 2, 'o', 'belly'], ['box', 'uni', 1, 'grin', 'belly'], ['ghost', 'horns', 2, 'smile', 'spots']
  ];
  const BODY = {
    blob: 'M60 22C88 22 103 42 103 68C103 94 85 108 60 108C35 108 17 94 17 68C17 42 32 22 60 22Z',
    egg: 'M60 14C84 14 97 38 97 66C97 95 81 109 60 109C39 109 23 95 23 66C23 38 36 14 60 14Z',
    box: 'M50 24H70C90 24 100 35 100 55V82C100 99 90 108 72 108H48C30 108 20 99 20 82V55C20 35 30 24 50 24Z',
    ghost: 'M21 62C21 35 38 18 60 18C82 18 99 35 99 62V101C93 109 86 109 80 102C75 96 70 96 66 102C62 108 58 108 54 102C50 96 45 96 40 102C34 109 27 109 21 101Z'
  };
  const TOPY = { blob: 22, egg: 14, box: 24, ghost: 18 };
  const eye = (x, y, r, k) => `<g class="ke"><ellipse cx="${x}" cy="${y}" rx="${r}" ry="${r * 1.08}" fill="#fff"/><ellipse cx="${x}" cy="${y}" rx="${r}" ry="${r * 1.08}" fill="none" stroke="#2b2d55" stroke-opacity=".12" stroke-width="1.4"/>`
    + `<circle class="kp" cx="${x + r * .12}" cy="${y + r * .12}" r="${r * .56}" fill="#2b2d55"/><circle cx="${x - r * .14}" cy="${y - r * .2}" r="${r * .22}" fill="#fff"/><circle cx="${x + r * .3}" cy="${y + r * .32}" r="${r * .09}" fill="#fff" opacity=".8"/>`
    + `<rect class="kl" x="${x - r - 1}" y="${y - r * 1.1 - 1}" width="${2 * r + 2}" height="${2.2 * r + 2}" rx="${r}" fill="${k}" transform="scale(1 0)" style="transform-box:fill-box;transform-origin:top"/></g>`;
  function svg(i, cls = '') {
    i = ((i | 0) % SET.length + SET.length) % SET.length;
    const [c, d, l] = PAL[i], [sh, top, ne, mo, ex] = SET[i], id = 'ka' + i, ty = TOPY[sh];
    let t = '';
    if (top === 'horns') t = `<path d="M38 ${ty + 12}C30 ${ty - 2} 31 ${ty - 12} 37 ${ty - 16}C38 ${ty - 6} 43 ${ty + 2} 50 ${ty + 6}Z" fill="#fff4dc"/><path d="M82 ${ty + 12}C90 ${ty - 2} 89 ${ty - 12} 83 ${ty - 16}C82 ${ty - 6} 77 ${ty + 2} 70 ${ty + 6}Z" fill="#fff4dc"/><path d="M38 ${ty + 12}C33 ${ty + 4} 32 ${ty - 4} 34 ${ty - 10}" fill="none" stroke="#e8d3a6" stroke-width="2" stroke-linecap="round"/><path d="M82 ${ty + 12}C87 ${ty + 4} 88 ${ty - 4} 86 ${ty - 10}" fill="none" stroke="#e8d3a6" stroke-width="2" stroke-linecap="round"/>`;
    else if (top === 'antenna') t = `<path d="M60 ${ty + 4}C60 ${ty - 6} 64 ${ty - 12} 70 ${ty - 16}" fill="none" stroke="${d}" stroke-width="4" stroke-linecap="round"/><circle cx="71" cy="${ty - 17}" r="7" fill="#ffd84d"/><circle cx="69" cy="${ty - 19}" r="2.4" fill="#fff" opacity=".9"/>`;
    else if (top === 'ears') t = `<path d="M30 ${ty + 22}C24 ${ty + 2} 28 ${ty - 10} 34 ${ty - 12}C42 ${ty - 6} 48 ${ty + 2} 52 ${ty + 8}Z" fill="${c}"/><path d="M90 ${ty + 22}C96 ${ty + 2} 92 ${ty - 10} 86 ${ty - 12}C78 ${ty - 6} 72 ${ty + 2} 68 ${ty + 8}Z" fill="${c}"/><path d="M34 ${ty + 12}C32 ${ty + 2} 33 ${ty - 4} 36 ${ty - 5}C40 ${ty - 2} 43 ${ty + 2} 45 ${ty + 6}Z" fill="${l}"/><path d="M86 ${ty + 12}C88 ${ty + 2} 87 ${ty - 4} 84 ${ty - 5}C80 ${ty - 2} 77 ${ty + 2} 75 ${ty + 6}Z" fill="${l}"/>`;
    else if (top === 'tuft') t = `<path d="M46 ${ty + 6}C44 ${ty - 6} 50 ${ty - 12} 54 ${ty - 12}C52 ${ty - 6} 54 ${ty - 2} 58 ${ty + 2}C58 ${ty - 10} 64 ${ty - 16} 70 ${ty - 14}C66 ${ty - 8} 66 ${ty - 2} 68 ${ty + 4}C70 ${ty - 2} 76 ${ty - 4} 80 ${ty - 2}C76 ${ty + 2} 74 ${ty + 6} 74 ${ty + 10}Z" fill="${d}"/>`;
    else if (top === 'uni') t = `<path d="M54 ${ty + 4}L61 ${ty - 22}L68 ${ty + 4}Z" fill="#ffe27a"/><path d="M56 ${ty - 4}L66 ${ty - 7}M58 ${ty - 12}L64 ${ty - 14}" stroke="#f2b705" stroke-width="2.2" stroke-linecap="round"/>`;
    const ey = ty + (sh === 'egg' ? 32 : 28);
    let e = '';
    if (ne === 1) e = eye(60, ey + 2, 15, c);
    else if (ne === 2) e = eye(46, ey, 10.5, c) + eye(74, ey, 10.5, c);
    else e = eye(42, ey + 3, 8.5, c) + eye(60, ey - 5, 9.5, c) + eye(78, ey + 3, 8.5, c);
    const my = ey + (ne === 1 ? 26 : 22);
    let m = '';
    if (mo === 'grin') m = `<path d="M44 ${my}C48 ${my + 15} 72 ${my + 15} 76 ${my}Z" fill="#3a1d3f"/><path d="M50 ${my + 7}C55 ${my + 12} 65 ${my + 12} 70 ${my + 7}C66 ${my + 5} 54 ${my + 5} 50 ${my + 7}Z" fill="#ff7a93"/><path d="M47 ${my}H73L72 ${my + 4}H48Z" fill="#fff"/>`;
    else if (mo === 'smile') m = `<path d="M48 ${my}C52 ${my + 9} 68 ${my + 9} 72 ${my}" fill="none" stroke="#3a1d3f" stroke-width="3.6" stroke-linecap="round"/>`;
    else if (mo === 'o') m = `<ellipse cx="60" cy="${my + 4}" rx="6" ry="7" fill="#3a1d3f"/><ellipse cx="60" cy="${my + 7}" rx="3.6" ry="3" fill="#ff7a93"/>`;
    else m = `<path d="M46 ${my}C50 ${my + 11} 70 ${my + 11} 74 ${my}Z" fill="#3a1d3f"/><path d="M52 ${my + 1}L55 ${my + 7}L58 ${my + 1.5}Z" fill="#fff"/><path d="M64 ${my + 1.5}L67 ${my + 7}L70 ${my + 1}Z" fill="#fff"/>`;
    const cheeks = `<ellipse cx="${ne === 3 ? 30 : 33}" cy="${my - 1}" rx="7" ry="4.5" fill="#ff6f91" opacity=".35"/><ellipse cx="${ne === 3 ? 90 : 87}" cy="${my - 1}" rx="7" ry="4.5" fill="#ff6f91" opacity=".35"/>`;
    const belly = ex === 'belly' ? `<ellipse cx="60" cy="${sh === 'ghost' ? 86 : 90}" rx="22" ry="14" fill="${l}" opacity=".9"/>`
      : `<circle cx="33" cy="84" r="5" fill="${d}" opacity=".45"/><circle cx="87" cy="78" r="4" fill="${d}" opacity=".45"/><circle cx="80" cy="96" r="3" fill="${d}" opacity=".45"/><circle cx="40" cy="98" r="3.4" fill="${d}" opacity=".45"/>`;
    const arms = `<path d="M${sh === 'egg' ? 25 : 20} 74C10 72 6 82 12 88C16 84 20 82 ${sh === 'egg' ? 26 : 21} 84Z" fill="${d}"/><path d="M${sh === 'egg' ? 95 : 100} 74C110 72 114 82 108 88C104 84 100 82 ${sh === 'egg' ? 94 : 99} 84Z" fill="${d}"/>`;
    const feet = sh === 'ghost' ? '' : `<ellipse cx="45" cy="108" rx="10" ry="5.5" fill="${d}"/><ellipse cx="75" cy="108" rx="10" ry="5.5" fill="${d}"/>`;
    return `<svg class="kava ${cls}" viewBox="-8 -16 136 136" aria-hidden="true"><defs><radialGradient id="${id}g" cx="38%" cy="30%" r="78%"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset=".28" stop-color="${c}" stop-opacity="0"/><stop offset="1" stop-color="${d}" stop-opacity=".55"/></radialGradient></defs>`
      + `<g class="kb">${t}${arms}${feet}<path d="${BODY[sh]}" fill="${c}"/><path d="${BODY[sh]}" fill="url(#${id}g)"/>${belly}`
      + `<path d="${BODY[sh]}" fill="none" stroke="${d}" stroke-opacity=".35" stroke-width="2"/>${cheeks}${e}${m}</g></svg>`;
  }
  return { svg, n: SET.length, color: i => PAL[((i | 0) % 12 + 12) % 12] };
})();
