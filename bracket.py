from get_games import get_games

games = get_games()

class Table(object):
  def __init__(self):
    self.data = [[]]

  def __getitem__(self, (x,y)):
    return self.data[y][x]

  def __setitem__(self, (x,y), val):
    try:
      self.data[y][x] = val
    except IndexError:
      self.resize(x, y)
      self.data[y][x] = val
    except:
      print y, x
      raise

  #we're fine with *horrible* efficiency in this particular app
  def resize(self, x, y):
    for i in range(y - len(self.data) + 1):
      self.data.append([])
    for row in self.data:
      for i in range(x - len(row) + 1):
        row.append(None)

  def __repr__(self):
    return self.data.__repr__()

  def tableize(self):
    o = []
    for y, row in enumerate(self.data):
      o.append("<tr>")
      for x, elt in enumerate(row):
        if x == 0:
          #TODO: 16v17
          pass
        elif not elt: o.append('<td class="none"></td>')
        elif elt.rows[0] == y: 
          if x == 1:
            o.append('''<td class="top" width="200">%s. <span class="round-%s game-%s"
                            >%s (%s)</span></td>''' % (
              elt.seed1, elt.round, elt.gameno, elt.team1[0], elt.team1[1]))
          else:
            o.append('''<td class="top" width="180">&nbsp;<span
                            class="round-%s game-%s"></span>''' % (
              elt.round, elt.gameno))
        elif elt.rows[1] == y:
          if x in (0,1):
            o.append('''<td class="bottom">%s. <span class="round-%s game-%s"
                            >%s (%s)</span></td>''' % (
              elt.seed2, elt.round, elt.gameno, elt.team2[0], elt.team2[1]))
          else:
            o.append('''<td class="bottom">&nbsp;<span class="round-%s game-%s"></span>''' % (
              elt.round, elt.gameno))
        else:
          o.append('<td class="middle">&nbsp;</td>')
    return '\n'.join(o)
    
t = Table()

#insert the games into the table in the proper spot
row = 0
for region in ("Midwest", "West", "East", "South"):
  for g in [x for x in games if x.round==1 and x.region==region]:
    g.rows = [row, row+2]
    t[1, row] = g
    t[1, row+1] = g
    t[1, row+2] = g
    g.child.rows[1 if g.child.rows[0] else 0] = row+1
    row += 3

  for round in (2,3,4):
    for g in [x for x in games if x.round==round and x.region==region]:
      miny, maxy = g.rows
      for i in range(0, maxy - miny + 1):
        t[round, miny + i] = g
        g.child.rows[1 if g.child.rows[0] else 0] = miny + int(ceil(float(maxy-miny)/2))

ff1.rows = [12, 36]
for i in range(12,37): t[5, i] = ff1
ff2.rows = [60, 84]
for i in range(60,85): t[5, i] = ff2
c.rows = [25, 72]
for i in range(25,73): t[6, i] = c
winner.rows = [50, 51]
t[7, 50] = winner

out = file("out.html", "w")
#TODO: if you change a team in an early game, update later games
#TODO: color teams based on pythagorean diff
#TODO: better randomizer
out.write("""
<html><head><title>Bill Mill Bracket Randomizer</title>
<script src="js/jquery-1.3.2.min.js" type="text/javascript"></script>
<link type="text/css" href="css/ui-lightness/jquery-ui-1.7.2.custom.css" rel="stylesheet" />    
<script type="text/javascript" src="js/jquery-ui-1.7.2.custom.min.js"></script>

<script>
rounds = {0:0, 1: 32, 2: 48, 3:56, 4:60, 5:62, 6:63};

function handleClick(that) {
  var atts = that.attr("class");
  var game = parseFloat(atts.match(/game-(\d+)/)[1]);
  var round = parseFloat(atts.match(/round-(\d+)/)[1]);
  var game_parity = (game - rounds[round-1]) % 2 == 0 ? 1 : 0;
  if (round < 4) {
    var nextgame = (Math.ceil((game-rounds[round-1])/2) + rounds[round]).toString();
    var firstorlast = game_parity ? ":last" : ":first";
  }
  else {
    if (game == 59 || game==57) {
      var nextgame = 61;
      var firstorlast = game == 59 ? ":first" : ":last";
    }
    else if (game==58 || game==60) {
      var nextgame = 62;
      var firstorlast = game == 58 ? ":first" : ":last";
    }
    else if (game == 61 || game == 62) {
      var nextgame = 63;
      var firstorlast = game == 61 ? ":first" : ":last";
    }
    else if (game == 63) {
      var nextgame = 64;
      var firstorlast = ":first";
    }
  }
  that.click(function() {
    //console.log("game, round, nextgame, (g-r[r-1]) ", game, round, nextgame, game - rounds[round-1], firstorlast);
    $(".game-" + nextgame + firstorlast).html(that.html());
  });
}

function randomize() {
  for (i=0; i < 7; i++) {
    $("td.top > span.round-" + i).each(function(_) {
      var that = $(this);
      var atts = that.attr("class");
      var game = atts.match(/game-\d+/)[0];
      var opp = $("." + game + ":last");
      function parsepoints(obj) {
        p = obj.html().match(/(.*?) \((.\d+), (\d+\.\d+), (\d+\.\d+)/);
        return [p[1], parseFloat(p[2]), parseFloat(p[3]), parseFloat(p[4])]
      }
      var topp = parsepoints(that);
      var oppp = parsepoints(opp);

      var favorite = topp[1] > oppp[1] ? that : opp;
      var underdog = topp[1] < oppp[1] ? that : opp;

      var a = parsepoints(favorite)[1];
      var b = parsepoints(underdog)[1];

      //use the log5 formula
      var log5 = (a - a * b) / (a + b - 2 * a * b);

      var pct = (log5 - .5) * 2;
      var green = "#00" + parseInt(255 * pct).toString(16) + "00";
      var red = "#" + parseInt(255 * pct).toString(16) + "0000";
      favorite.css("color", green);
      underdog.css("color", red);

      //console.log(topp[0] + " vs " + oppp[0] + " %: ", log5);
      
      if (amount_of_randomness == 0) {
        favorite.click();
      }
      else {
        for (j=0; j < (4-amount_of_randomness); j++) {
          fav_wins = false;
          if (log5 > Math.random()) {
            favorite.click();
            fav_wins = true;
            break;
          }
        }
        if (!fav_wins) {
          underdog.click();
        }
      }
    });
  }
}

$(document).ready(function() {
  for (i=0; i < 8; i++) {
    $(".round-" + i).each(function(i) { handleClick($(this)); });
  }
  $("td.top > span.round-1").each(function(i) { $(this).parent().css("height", "30px").css("vertical-align", "bottom"); })
  $("#randomize").click(function() { randomize(); });

  amount_of_randomness = 3;

  // Slider
  $('#slider').slider({
    min: 0,
    max: 3,
    step: 1,
    value: amount_of_randomness,
    slide: function(event, ui) {
      amount_of_randomness = parseInt(ui.value);
      //console.log("amount of randomness:", amount_of_randomness, ui);
      var labels = ["None", "Almost None", "Some", "Lots"];
      $("#desc").html(labels[amount_of_randomness])
    }
  });
});
</script>
<style>
.top {  border-bottom: 1px solid #aaaaaa; padding: 0px 5px 0px 5px; }
.bottom { border-bottom: 1px solid #aaaaaa; border-right: 1px solid #aaaaaa; padding: 0px 5px 0px 5px; }
.middle { border-right: 1px solid #aaaaaa; padding: 0px 5px 0px 5px; }
tr { padding-bottom: 10px; font-size: 12px; }
span { cursor: pointer; }
#slider { width: 200px; }
body { font: 16px serif; }
/* fix the jquery UI text size changing */
#text { font: 16px serif; padding-right: 20px;}
#desc { margin-left: 20px; }
</style>
</head>
<body>
<p>Check out the <a href="http://billmill.org/ncaa_randomizer.html">blog article explaining what this is about</a>.
<p><table><tr><td id="text">Randomness:</td><td><div id="slider"></div></td><td id="text"><span id="desc">Lots</span></td></tr></table>
<p><input type="submit" id="randomize" value="randomize"><table cellspacing=0 width=1200 style='table-layout:fixed'>
""")
out.write(t.tableize())
out.write("</table></body></html>")
out.close()
