$file = 'C:\Users\Luis Rojas\.openclaw\workspace\paper\references.bib'
$t = [System.IO.File]::ReadAllText($file, [System.Text.Encoding]::UTF8)

$bs = '\'  # backslash
$dq = '"'  # double-quote

# Helper: replace a Unicode char (by code point) with a LaTeX string
function Rep([string]$s, [int]$cp, [string]$latex) {
    return $s.Replace([string][char]$cp, $latex)
}

# Uppercase accented
$t = Rep $t 0x00C1 ($bs + "'{A}")
$t = Rep $t 0x00C9 ($bs + "'{E}")
$t = Rep $t 0x00CD ($bs + "'{I}")
$t = Rep $t 0x00D3 ($bs + "'{O}")
$t = Rep $t 0x00DA ($bs + "'{U}")
$t = Rep $t 0x00C3 ($bs + "~{A}")
$t = Rep $t 0x00C2 ($bs + "^{A}")
$t = Rep $t 0x00C7 ($bs + "c{C}")
$t = Rep $t 0x00D6 ($bs + $dq + "{O}")
$t = Rep $t 0x00DC ($bs + $dq + "{U}")
$t = Rep $t 0x00C4 ($bs + $dq + "{A}")

# Lowercase accented
$t = Rep $t 0x00E1 ($bs + "'{a}")
$t = Rep $t 0x00E9 ($bs + "'{e}")
$t = Rep $t 0x00ED ($bs + "'{i}")
$t = Rep $t 0x00F3 ($bs + "'{o}")
$t = Rep $t 0x00FA ($bs + "'{u}")
$t = Rep $t 0x00E0 ($bs + "`{a}")
$t = Rep $t 0x00E8 ($bs + "`{e}")
$t = Rep $t 0x00E2 ($bs + "^{a}")
$t = Rep $t 0x00EA ($bs + "^{e}")
$t = Rep $t 0x00F4 ($bs + "^{o}")
$t = Rep $t 0x00E3 ($bs + "~{a}")
$t = Rep $t 0x00F5 ($bs + "~{o}")
$t = Rep $t 0x00F1 ($bs + "~{n}")
$t = Rep $t 0x00E7 ($bs + "c{c}")
$t = Rep $t 0x00E6 ($bs + "ae")
$t = Rep $t 0x00F6 ($bs + $dq + "{o}")
$t = Rep $t 0x00FC ($bs + $dq + "{u}")
$t = Rep $t 0x00EB ($bs + $dq + "{e}")
$t = Rep $t 0x00EF ($bs + $dq + "{i}")
$t = Rep $t 0x00E4 ($bs + $dq + "{a}")

# Latin Extended-A
$t = Rep $t 0x0105 ($bs + "k{a}")
$t = Rep $t 0x0107 ($bs + "'{c}")
$t = Rep $t 0x0144 ($bs + "'{n}")
$t = Rep $t 0x015F ($bs + "c{s}")
$t = Rep $t 0x017E ($bs + "v{z}")

# Punctuation / typography
$t = Rep $t 0x2013 '--'
$t = Rep $t 0x2014 '---'
$t = Rep $t 0x2019 "'"
$t = Rep $t 0x201C "''"
$t = Rep $t 0x201D "''"
$t = Rep $t 0x00A0 ' '
$t = Rep $t 0x223C ($bs + 'textasciitilde{}')
$t = Rep $t 0xFFFD ''

# Fix Vietnamese Nguyen: after tilde substitution => "Nguy\textasciitilde{}n"
$t = $t.Replace(($bs + 'textasciitilde{}n'), ($bs + '~{e}n'))

[System.IO.File]::WriteAllText($file, $t, [System.Text.UTF8Encoding]::new($false))
Write-Host 'Saved.'

# Check remaining non-ASCII
$remaining = $t.ToCharArray() | Where-Object { [int]$_ -gt 127 } | ForEach-Object { 'U+' + ([int]$_).ToString('X4') } | Sort-Object -Unique
Write-Host ('Remaining non-ASCII: ' + $remaining.Count)
$remaining
