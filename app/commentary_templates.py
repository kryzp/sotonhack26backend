import random

TEMPLATES: dict[str, list[str]] = {

	# ── 1. GAME CREATED ──
	"game_created": [
		"A new game has entered the arena! Get your teams ready!",
		"Game lobby is OPEN! Gather round, gather round!",
		"Fresh game, fresh chaos. Who's ready to embarrass themselves?",
		"Welcome to the lobby! The calm before the storm.",
		"A new challenger approaches! Well, a new game. Same energy.",
		"Lobby created! Time to pick your sides and prepare for battle.",
		"The stage is set! Now we just need some brave souls to play.",
		"Game room is live! Tell your friends. Or your enemies. Even better.",
		"Welcome, welcome! Another round of people trying to sound smart!",
		"New game alert! The word connecting arena awaits!",
		"A fresh battlefield! Who will emerge victorious tonight?",
		"Game created! Grab a drink, grab a seat, and prepare to judge everyone.",
		"We're live! Well, the lobby is. The chaos starts soon.",
		"Another game, another chance to prove you're the smartest person in the room.",
		"The arena is ready! Are you?",
	],

	# ── 2. GAME STARTED ──
	"game_started": [
		"Welcome to Unconventional Connections! {team_left} versus {team_right}. Let's see who's got the brains tonight.",
		"Alright folks, it's {team_left} against {team_right}. Zero mercy. Let's go!",
		"The game is ON! {team_left} and {team_right}, prepare for mental gymnastics!",
		"Ladies and gentlemen, {team_left} versus {team_right}! Try not to embarrass yourselves.",
		"It's showtime! {team_left} and {team_right} are about to prove that literally anything can be connected.",
		"Let the battle of wits begin! {team_left} versus {team_right}!",
		"And we're OFF! {team_left} and {team_right}, may the cleverest team win!",
		"The gloves are off! {team_left} versus {team_right}! Let's get weird.",
		"Game time! {team_left} and {team_right}, show us what those brains can do!",
		"We are LIVE! {team_left} against {team_right}! This is going to be beautiful.",
		"Three rounds. Two teams. One winner. {team_left} versus {team_right}. LET'S GO!",
		"Welcome, welcome! {team_left} and {team_right} are about to make some questionable connections!",
		"It's {team_left} versus {team_right}! Place your bets now!",
		"The starting pistol has fired! Well, metaphorically. {team_left} versus {team_right}!",
		"Get ready for some truly creative mental gymnastics from {team_left} and {team_right}!",
	],

	# ── 3. ROUND STARTED ──
	"round_started": [
		"Round {round_number}! Here we go!",
		"Alright, round {round_number} of {total_rounds}!",
		"Round {round_number}! Let's see what the word gods have cooked up!",
		"Next round! Round {round_number}! Buckle up!",
		"Moving on to round {round_number}!",
		"It's round {round_number} time!",
		"Round {round_number}! Things are heating up!",
		"And we're on to round {round_number}! Ready?",
	],

	# ── 3b. WORDS PRESENTED (dedicated word reveal with dramatic pause) ──
	"words_presented": [
		"Your first word is... {word_one}! ... And your second word is... {word_two}! ... Good luck connecting THOSE!",
		"Word number one... {word_one}! ... Word number two... {word_two}! ... Yeah, I don't see it either.",
		"The first word is... {word_one}! ... And the second word is... {word_two}! ... My condolences.",
		"Alright! Your words are... {word_one}! ... aaand... {word_two}! ... If you can connect those, you deserve a trophy. Or therapy.",
		"Here they come! First up... {word_one}! ... And then... {word_two}! ... What could they POSSIBLY have in common?",
		"Drumroll please! Word one... {word_one}! ... Word two... {word_two}! ... Even I'm stumped on this one.",
		"Presenting! Your first word... {word_one}! ... Your second word... {word_two}! ... This is either genius or disaster in the making.",
		"Listen up! The words are... {word_one}! ... aaand... {word_two}! ... I genuinely want to see how you pull this off.",
		"OH this is a good one! First word... {word_one}! ... Second word... {word_two}! ... SPICY!",
		"The word gods have spoken! First... {word_one}! ... Second... {word_two}! ... Figure it out!",
		"Ready? Your first word is... {word_one}! ... Your second word is... {word_two}! ... No pressure. Actually, ALL the pressure.",
		"OK OK OK! Word one is... {word_one}! ... And word two is... {word_two}! ... The writers are clearly out to get you.",
	],

	# ── 4. BUZZ OPENED ──
	"buzz_opened": [
		"Buzzers are OPEN! Smash that button!",
		"The buzzers are live! First one in gets the glory!",
		"BUZZ BUZZ BUZZ! Buzzers are open, people!",
		"Fingers on buzzers! Who's feeling brave?",
		"Buzzers are HOT! Step right up!",
		"The floor is open! Who dares to buzz?",
		"Alright, buzzers are ready! Show me what you've got!",
		"Buzzers unlocked! It's anyone's game!",
		"Time to buzz! Who thinks they can do it?",
		"The buzzers await! Be fast, be bold, be first!",
		"Buzzer time! Don't be shy!",
		"And the buzzers are LIVE! Who's going in?",
		"Ready, set, BUZZ! Buzzers are open!",
		"Buzzers on! The race begins NOW!",
		"Step up or shut up! Buzzers are open!",
	],

	# ── 5. BUZZ LOCKED ──
	"buzz_locked": [
		"{player_name} slams the buzzer! Brave. Possibly stupid. Let's find out.",
		"{player_name} is going for it! The pressure is ON.",
		"And {player_name} buzzes in! Either they've got it, or they're bluffing.",
		"{player_name} with the buzzer! Confidence level: maximum.",
		"BUZZ! {player_name} wants the spotlight. Don't choke!",
		"{player_name} hits the buzzer first! This better be good.",
		"Lightning reflexes from {player_name}! Now back it up!",
		"{player_name} buzzes in with AUTHORITY! Let's see if the brain matches the speed.",
		"And it's {player_name}! The buzzer is LOCKED!",
		"{player_name} slaps that buzzer! Bold move! Let's see if it pays off.",
		"WOW! {player_name} with the instant buzz! Someone's feeling confident!",
		"{player_name} jumps on the buzzer! No hesitation! I respect that.",
		"LOCKED IN! {player_name} claims the buzzer! Time to deliver!",
		"{player_name} goes for it! The crowd holds its breath!",
		"{player_name} with the quick draw! Now let's see the quick wit!",
		"BAM! {player_name} on the buzzer! This is their moment!",
	],

	# ── 6. SIDE SELECTED ──
	"side_selected": [
		"Playing for team {side}! Let's see what they've got!",
		"Team {side} is up! The pressure is on!",
		"Representing team {side}! Make it count!",
		"It's team {side}'s moment! Don't waste it!",
		"Team {side} steps up to the plate!",
		"Going in for team {side}! Show us something special!",
		"Team {side} is in the hot seat! Let's go!",
		"Locked in for team {side}! Time to shine!",
		"Team {side} takes the challenge! Bold choice!",
		"Playing for team {side}! No pressure at all. Just kidding. ALL the pressure.",
		"Team {side} sends their champion! Make it legendary!",
		"And they're playing for team {side}! Here we go!",
		"Team {side} is on the clock! Make every second count!",
		"Fighting for team {side}! The crowd awaits!",
		"Team {side} has entered the arena! Let's hear what they've got!",
	],

	# ── 8. VALIDATION STARTED ──
	"validation_started": [
		"Let's see what the judge thinks!",
		"Sending to the AI judges! Pray.",
		"The verdict is being calculated! Fingers crossed!",
		"Gemini is deliberating! This could go either way!",
		"And now we wait for the judges!",
		"Validation in progress! The tension is unbearable!",
		"The AI is thinking! Which is more than I can say for that answer!",
		"Hold your breath, everyone! The judges are reviewing!",
		"To the judges we go! May the odds be in your favor!",
		"Submitting to the oracle! Let's see the truth!",
		"The AI ponders your answer! Dramatically, of course!",
		"Judgment incoming! Brace yourselves!",
		"Sending it off for validation! Did they nail it?",
		"The judge's chambers are deliberating! Nobody move!",
		"And now, the moment of truth! Let the AI decide your fate!",
	],

	# ── 9. VALIDATION COMPLETE (VALID) ──
	"validation_valid": [
		"{reason}. That's {steps} steps! Points to team {selected_side}!",
		"VALID! {steps} steps! {reason}",
		"The judges say YES! {steps} steps! {reason}",
		"Incredible! {reason}. {steps} steps for team {selected_side}!",
		"IT COUNTS! {steps} steps! {reason}",
		"Connection accepted! {steps} steps! {reason}",
		"The AI approves! {reason}. {steps} steps awarded!",
		"BRILLIANT! That's {steps} steps! {reason}",
		"And it's GOOD! {steps} steps for team {selected_side}! {reason}",
		"The judges are impressed! {steps} steps! {reason}",
		"Valid connection! {reason}. {steps} steps on the board!",
		"That's a VALID chain! {steps} steps! {reason}",
		"Nailed it! {steps} steps! {reason}",
		"The connection holds! {steps} steps to team {selected_side}! {reason}",
		"Accepted! {reason}. {steps} steps earned!",
	],

	# ── 10. VALIDATION COMPLETE (INVALID) ──
	"validation_invalid": [
		"Oh no. That did NOT land. {reason}",
		"Yikes. The AI says no. {reason}",
		"INVALID! {reason}. Better luck next time!",
		"That's a swing and a miss! {reason}",
		"Not even close! {reason}",
		"The judges say NO! {reason}",
		"Rejected! {reason}. Ouch!",
		"Connection DENIED! {reason}",
		"That's a no from the judges! {reason}",
		"Oh dear. {reason}. Zero points!",
		"The AI is not impressed. {reason}",
		"INVALID connection! {reason}. Back to the drawing board!",
		"The chain breaks! {reason}. No points this round!",
		"That's going to hurt! {reason}. Invalid!",
		"Nope! The judges have spoken! {reason}",
	],

	# ── 11. GAME FINISHED (WINNER) ──
	"game_finished": [
		"And that's the game! {winner} takes it! What a match!",
		"Game over! {winner} wins! Fewer steps means bigger brain!",
		"It's done! Congratulations to {winner}! The other team, well, you tried.",
		"Final score: {team_left} with {team_left_score}, {team_right} with {team_right_score}. {winner} wins!",
		"And we have a winner! {winner} claims victory!",
		"GAME! SET! MATCH! {winner} is your champion!",
		"{winner} wins the whole thing! Take a bow!",
		"That's all folks! {winner} takes the crown!",
		"Victory belongs to {winner}! What a performance!",
		"The game is OVER! {winner} wins it all!",
		"And just like that, {winner} is victorious! Well played!",
		"Congratulations {winner}! You've proven your brain is slightly less smooth than your opponent's!",
		"{winner} is the champion! The crowd goes WILD!",
		"Final whistle! {winner} wins with superior connections!",
		"And there it is! {winner} wins! Someone get them a trophy!",
	],

	# ── 12. GAME FINISHED (TIE) ──
	"game_finished_tie": [
		"It's a tie! Both teams are equally brilliant. Or equally terrible. Hard to tell.",
		"A perfect tie! Neither team could pull ahead! Respect!",
		"Dead even! Looks like we need a rematch!",
		"TIE GAME! Both teams finish with the same score! Incredible!",
		"It's a draw! Both teams are perfectly matched!",
		"Nobody wins! Or everybody wins! Depends on your perspective!",
		"A tie! The rarest of outcomes! Both teams take a bow!",
		"Equal scores! The universe demands a rematch!",
		"It's a DEAD HEAT! Both teams are unstoppable! Or very stoppable! Same thing!",
		"Tied up! Neither team could seal the deal! That's either impressive or tragic!",
		"A perfect tie! Both teams share the glory! And the shame!",
		"Draw! The AI couldn't separate you! That's actually kind of beautiful!",
		"It's a tie game! Both teams are champions! Or both are losers! Your call!",
		"Dead level! Wow! Both teams gave it everything!",
		"And it ends in a TIE! I genuinely did not see that coming!",
	],
}


def get_commentary(event: str, context: dict) -> str:
	if event == "validation_complete":
		if context.get("valid", True):
			event = "validation_valid"
		else:
			event = "validation_invalid"

	#tie vs winner
	if event == "game_finished" and context.get("winner") == "tie":
		event = "game_finished_tie"
	elif event == "game_finished":
		winner = context.get("winner", "")
		if winner == "left":
			context["winner"] = context.get("team_left", "Team Left")
		elif winner == "right":
			context["winner"] = context.get("team_right", "Team Right")

	templates = TEMPLATES.get(event, [
		"And we're moving on!",
		"Things are happening! Exciting things!",
		"Well, that was something.",
	])

	template = random.choice(templates)

	try:
		return template.format(**context)
	except KeyError:
		return random.choice([
			"The game continues!",
			"Things are getting interesting!",
			"And the crowd goes wild!",
		])
