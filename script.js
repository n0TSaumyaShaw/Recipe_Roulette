/**
 * Recipe Roulette: Shinchan Edition
 * Plain Vanilla JavaScript, zero dependencies
 */

// 1. Hated Ingredients Array (easy to edit)
const HATED_INGREDIENTS = ['green pepper', 'piman', 'capsicum', 'eggplant', 'brinjal'];

// 2. Default Pantry Staples (assumed always available)
const PANTRY_STAPLES = ['salt', 'oil', 'water', 'spices', 'butter', 'sugar', 'pepper', 'turmeric'];

// 3. Preset Tappable Chips
const DEFAULT_CHIPS = [
  { name: 'eggs', label: 'Eggs', emoji: '🥚' },
  { name: 'onion', label: 'Onion', emoji: '🧅' },
  { name: 'bread', label: 'Bread', emoji: '🍞' },
  { name: 'rice', label: 'Rice', emoji: '🍚' },
  { name: 'tomato', label: 'Tomato', emoji: '🍅' },
  { name: 'potato', label: 'Potato', emoji: '🥔' },
  { name: 'cheese', label: 'Cheese', emoji: '🧀' },
  { name: 'milk', label: 'Milk', emoji: '🥛' },
  { name: 'curd', label: 'Curd', emoji: '🥣' },
  { name: 'paneer', label: 'Paneer', emoji: '🧈' },
  { name: 'noodles', label: 'Noodles', emoji: '🍜' },
  { name: 'chilli', label: 'Chilli', emoji: '🌶️' },
  { name: 'banana', label: 'Banana', emoji: '🍌' },
  { name: 'green pepper', label: 'Green Pepper', emoji: '🫑' },
  { name: 'eggplant', label: 'Eggplant', emoji: '🍆' },
  { name: 'garlic', label: 'Garlic', emoji: '🧄' }
];

// 4. Misae & Shinchan Quips Collection
const QUIPS = {
  hatedGreenPepper: [
    "NOOO! Not the green pepper! Shinchan is leaving!",
    "PIMAN DETECTED! Emergency butt dance to escape the table!",
    "Why the green pepper?! Even Shiro won't touch this vegetable of doom!"
  ],
  hatedEggplant: [
    "NOOO! Eggplant?! Did Misae bribe you with department store coupons?!",
    "Purple vegetable of sadness! Shinchan's taste buds are going on strike!",
    "Eggplant alert! Quick, call Action Bastard for emergency evacuation!"
  ],
  specific: {
    eggs: "Ande ka funda! Even Shiro eats better than this, but omelette toh mast hai!",
    bread: "Bread again? Are we feeding the pigeons or Nohara Shinnosuke?!",
    noodles: "Maggi toh 2 minute mein banti hai, yeh chef kitna time lega?!",
    banana: "Kela power! High potassium for maximum butt-dance velocity!",
    cheese: "Cheese! Melting like Kazama when he gets a compliment from teacher!",
    potato: "Aloo is love, aloo is life! 100 times better than piman!",
    paneer: "Paneer? Aaj toh party hai! Dad ko bonus mil gaya kya?!",
    curd: "Dahi chawal khake mast 4 ghante so jaunga!",
    rice: "Chawal bina pet nahi bharta! Mummy, jaldi serve karo!",
    tomato: "Tamatar jaisa laal gaal ho jayega mera!",
    onion: "Pyaaz kaat te huye Shinchan rone ka natak karega!",
    chilli: "Mirchi lag gayi toh Shiro ke bowl ka paani pi jaunga!"
  },
  general: [
    "Chocobi counts as an ingredient, right? Put Chocobi in it!",
    "Mama, I'm hungry! Hurry before my stomach eats my spine!",
    "Quick! Misae is taking her afternoon nap, let's cook before she wakes up!",
    "Whatever we make, Shiro gets the first bite... just in case!",
    "Action Bastard power cooking in session! Hai-yaaa!",
    "Don't worry, 5-year-old culinary genius Nohara Shinnosuke is on the case!",
    "Hey hey, beautiful big sister, want to share this meal with Shinchan?",
    "If this turns out bad, we blame Hiroshi's smelly socks!",
    "Mummy ko mat batana maine extra cheese daal diya!",
    "Buri Buri Zaemon is watching our cooking technique!",
    "Aaj khane mein kuch aisa banao jo restaurant wale bhi sharma jayein!",
    "Himawari ke doodh ki bottle se pehle mera khana aana chahiye!",
    "Kazama ke tiffin se accha khana banana hai aaj!",
    "Masato aur Bo-chan ko bula lo, party shuru karte hain!",
    "Principal sir ke gusse jaisa spicy khana ban raha hai kya?!",
    "Kitna wait karwaoge? Chocobi ka packet khol raha hoon main!",
    "Pait mein chuhe wrestling kar rahe hain, jaldi karo!",
    "Action Kamen diet plan: 1 plate now, 3 plates later!",
    "Agar khana jal gaya toh Yoshinaga ma'am ko treat denge!",
    "Kasukabe Defense Force, dinner operation commence!"
  ],
  offlineMisae: "Internet gaya chhutti pe! Mummy's local survival cookbook to the rescue!"
};

// Sound Effects using Web Audio API (No external assets required)
let soundEnabled = true;
let audioCtx = null;

function getAudioContext() {
  if (!audioCtx) {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (AudioContextClass) audioCtx = new AudioContextClass();
  }
  if (audioCtx && audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
  return audioCtx;
}

function playSound(type) {
  if (!soundEnabled) return;
  try {
    const ctx = getAudioContext();
    if (!ctx) return;

    if (type === 'pop') {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(440, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.08);
      gain.gain.setValueAtTime(0.2, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.08);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.09);
    } else if (type === 'tick') {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'square';
      osc.frequency.setValueAtTime(600 + Math.random() * 200, ctx.currentTime);
      gain.gain.setValueAtTime(0.08, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.04);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.05);
    } else if (type === 'fanfare') {
      [523.25, 659.25, 783.99, 1046.5].forEach((freq, i) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(freq, ctx.currentTime + (i * 0.1));
        gain.gain.setValueAtTime(0.2, ctx.currentTime + (i * 0.1));
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + (i * 0.1) + 0.35);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(ctx.currentTime + (i * 0.1));
        osc.stop(ctx.currentTime + (i * 0.1) + 0.36);
      });
    } else if (type === 'angry') {
      [220, 196, 174, 146].forEach((freq, i) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(freq, ctx.currentTime + (i * 0.12));
        gain.gain.setValueAtTime(0.25, ctx.currentTime + (i * 0.12));
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + (i * 0.12) + 0.15);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(ctx.currentTime + (i * 0.12));
        osc.stop(ctx.currentTime + (i * 0.12) + 0.16);
      });
    }
  } catch (e) {
    // AudioContext blocked or not supported
  }
}

// State
const EMBEDDED_RECIPES = [
  {
    "id": "masala_omelette",
    "name": "Speedy Masala Omelette",
    "time": "5 mins",
    "difficulty": "Super Easy",
    "ingredients": ["eggs", "onion", "chilli", "tomato"],
    "optional_ingredients": ["cheese"],
    "steps": [
      "Whisk 2 eggs with a pinch of salt and turmeric in a mug.",
      "Finely chop onion, chilli, and tomato, then stir them right into the eggs.",
      "Heat oil or butter in a pan and pour the mixture evenly.",
      "Cook for 2 minutes, fold in half (throw cheese inside if you have it!), and flip once."
    ],
    "shinchan_comment": "Action Bastard power breakfast! Eggs make you strong like me!"
  },
  {
    "id": "french_toast",
    "name": "Sweet Comic French Toast",
    "time": "7 mins",
    "difficulty": "Easy",
    "ingredients": ["bread", "eggs", "milk"],
    "optional_ingredients": ["banana", "cheese"],
    "steps": [
      "Beat 1 egg with a splash of milk and a spoonful of sugar in a shallow dish.",
      "Dip bread slices on both sides until soaked but not soggy.",
      "Sizzle in a hot buttered pan until both sides are golden brown.",
      "Top with sliced banana or a cheeky pinch of cinnamon."
    ],
    "shinchan_comment": "Ooh lala! So soft and fluffy, just like Shiro's belly!"
  },
  {
    "id": "egg_fried_rice",
    "name": "Midnight Egg Fried Rice",
    "time": "8 mins",
    "difficulty": "Easy",
    "ingredients": ["rice", "eggs", "onion", "chilli"],
    "optional_ingredients": ["tomato", "cheese"],
    "steps": [
      "Scramble eggs in a hot pan with oil, then set aside in a bowl.",
      "Toss diced onions and chilli into the pan until fragrant and slightly crispy.",
      "Dump in cooked rice with soy sauce or salt, pepper, and chili powder.",
      "Toss the scrambled eggs back in over high heat for 1 minute."
    ],
    "shinchan_comment": "Wok hei mastered by 5-year-old prodigy Nohara Shinnosuke!"
  },
  {
    "id": "cheesy_bread_pizza",
    "name": "Tawa Bread Pizza",
    "time": "6 mins",
    "difficulty": "Super Easy",
    "ingredients": ["bread", "cheese", "tomato", "onion"],
    "optional_ingredients": ["chilli", "paneer"],
    "steps": [
      "Lightly toast one side of the bread on a dry tawa/pan.",
      "Flip over and spread tomato ketchup or crushed tomato with salt on the warm side.",
      "Scatter chopped onions, tomatoes, and generous cheese on top.",
      "Cover with a lid on low flame for 3 minutes until the cheese gets all melty."
    ],
    "shinchan_comment": "Pizza without waiting for delivery! Even Misae can't nag about this!"
  },
  {
    "id": "jeera_aloo",
    "name": "Crispy Spiced Jeera Aloo",
    "time": "10 mins",
    "difficulty": "Easy",
    "ingredients": ["potato", "chilli"],
    "optional_ingredients": ["onion", "tomato"],
    "steps": [
      "Boil or microwave diced potatoes until tender (3 mins in microwave with water).",
      "Heat 1 tbsp oil in a pan, toss in cumin seeds and slit chillies until crackling.",
      "Add potatoes, turmeric, red chilli powder, and salt.",
      "Pan-fry on medium-high until the potato edges turn golden and super crunchy."
    ],
    "shinchan_comment": "Potatoes are the best vegetable in the whole world! 100% better than green peppers!"
  },
  {
    "id": "curd_rice",
    "name": "Soothing Comfort Curd Rice",
    "time": "4 mins",
    "difficulty": "Super Easy",
    "ingredients": ["rice", "curd"],
    "optional_ingredients": ["chilli", "onion"],
    "steps": [
      "Mash cooked warm or leftover rice lightly with a fork.",
      "Mix thoroughly with fresh curd, a splash of water, and salt until creamy.",
      "For extra kick, quickly heat a teaspoon of oil with mustard seeds and chopped chilli.",
      "Pour the hot tempering over the cool curd rice and enjoy!"
    ],
    "shinchan_comment": "Cool down cool down! Perfect when Misae gives you the knuckle punch!"
  },
  {
    "id": "garlic_butter_noodles",
    "name": "Chilli Garlic Maggi/Noodles",
    "time": "6 mins",
    "difficulty": "Easy",
    "ingredients": ["noodles", "onion", "chilli"],
    "optional_ingredients": ["eggs", "cheese"],
    "steps": [
      "Boil noodles according to package and drain, reserving 3 spoons of noodle water.",
      "Sauté chopped onion and lots of chilli in butter or oil.",
      "Add tastemaker/seasoning powder with the reserved water to make a glossy sauce.",
      "Toss the noodles in and optionally melt a cheese cube on top."
    ],
    "shinchan_comment": "Slurrrrrrrp! Master noodle slurper Shinchan approves!"
  },
  {
    "id": "paneer_bhurji",
    "name": "5-Minute Paneer Bhurji",
    "time": "7 mins",
    "difficulty": "Easy",
    "ingredients": ["paneer", "onion", "tomato", "chilli"],
    "optional_ingredients": ["bread"],
    "steps": [
      "Crumble fresh paneer with your hands.",
      "Heat oil in a skillet, sauté chopped onions and green chilli until golden.",
      "Stir in chopped tomatoes, turmeric, and chilli powder until soft.",
      "Dump in crumbled paneer, stir gently for 2 minutes, and serve with bread."
    ],
    "shinchan_comment": "Rich and delicious! Makes me feel like a rich prince!"
  },
  {
    "id": "banana_pancake",
    "name": "2-Ingredient Banana Pancakes",
    "time": "6 mins",
    "difficulty": "Super Easy",
    "ingredients": ["banana", "eggs"],
    "optional_ingredients": ["milk", "cheese"],
    "steps": [
      "Mash 1 ripe banana in a bowl until smooth.",
      "Crack in 2 eggs and whisk vigorously until a batter forms.",
      "Pour small palm-sized rounds into a lightly buttered pan on medium-low.",
      "Flip carefully after 2 minutes once bubbles appear, cook 1 more minute."
    ],
    "shinchan_comment": "Sweet and bouncy! Almost as good as Chocobi!"
  },
  {
    "id": "egg_bhurji_toast",
    "name": "Street-Style Anda Bhurji Toast",
    "time": "6 mins",
    "difficulty": "Easy",
    "ingredients": ["eggs", "bread", "onion", "tomato"],
    "optional_ingredients": ["chilli", "cheese"],
    "steps": [
      "Sauté chopped onion, tomato, and chilli in 1 tbsp butter/oil.",
      "Crack 2 eggs directly into the pan and stir vigorously on medium heat.",
      "Season with salt and pepper until fluffy and softly cooked.",
      "Butter and toast the bread slices, then pile the bhurji high on top."
    ],
    "shinchan_comment": "Bhurji explosion! Keeps Shinchan energized for prank patrol!"
  },
  {
    "id": "tomato_rice",
    "name": "Tangy Spicy Tomato Rice",
    "time": "8 mins",
    "difficulty": "Easy",
    "ingredients": ["rice", "tomato", "onion", "chilli"],
    "optional_ingredients": ["potato"],
    "steps": [
      "Finely chop or crush tomatoes into a juicy pulp.",
      "Sauté onions and green chillies in oil until soft, then stir in the tomato pulp.",
      "Add salt, turmeric, and red chilli powder; simmer until oil glistens on top.",
      "Toss in cooked rice and gently fold together until bright ruby red."
    ],
    "shinchan_comment": "Bright red just like Action Bastard's cape! Hai-yaaa!"
  },
  {
    "id": "cheesy_potato_mash",
    "name": "Survival Cheesy Mashed Potatoes",
    "time": "8 mins",
    "difficulty": "Super Easy",
    "ingredients": ["potato", "cheese", "milk"],
    "optional_ingredients": ["onion", "chilli"],
    "steps": [
      "Peel, cube, and microwave potatoes in water for 5 minutes until fork-tender.",
      "Drain water, mash hot potatoes with a fork or spoon.",
      "Stir in warm milk, salt, pepper, and grate in as much cheese as you have.",
      "Whisk until velvety smooth and gooey."
    ],
    "shinchan_comment": "Warm potato hug! Misae won't let me eat only this, but nobody is watching!"
  },
  {
    "id": "egg_drop_soup",
    "name": "Dorm Egg Drop Noodle Soup",
    "time": "6 mins",
    "difficulty": "Easy",
    "ingredients": ["noodles", "eggs", "onion"],
    "optional_ingredients": ["chilli", "tomato"],
    "steps": [
      "Bring 2 cups of water to a rolling boil with noodle seasoning.",
      "Drop in noodles and sliced onions, cooking for 2 minutes.",
      "Lightly beat an egg in a small cup.",
      "Slowly drizzle the beaten egg into the simmering soup while swirling with chopsticks."
    ],
    "shinchan_comment": "Silky egg ribbons! Warms the tummy on cold Kasukabe nights!"
  },
  {
    "id": "chilli_cheese_toast",
    "name": "Crispy Chilli Cheese Toast",
    "time": "5 mins",
    "difficulty": "Super Easy",
    "ingredients": ["bread", "cheese", "chilli"],
    "optional_ingredients": ["onion", "tomato"],
    "steps": [
      "Mix grated cheese with finely chopped chillies and a tiny pinch of salt.",
      "Pile the cheesy chilli mix thickly onto bread slices.",
      "Place on a heated pan, cover with a steel plate or lid on low heat.",
      "Remove when cheese is bubbling and the bread bottom is golden and crunchy."
    ],
    "shinchan_comment": "Spicy cheesy crunch! Better than Hiroshi's smelly socks!"
  },
  {
    "id": "potato_onion_hash",
    "name": "Crispy Skillet Potato & Onion Hash",
    "time": "9 mins",
    "difficulty": "Easy",
    "ingredients": ["potato", "onion"],
    "optional_ingredients": ["eggs", "cheese"],
    "steps": [
      "Grate or finely slice raw potatoes and squeeze out excess moisture.",
      "Thinly slice onions and mix with potatoes, salt, and pepper.",
      "Press the mixture flat into a hot oiled skillet like a giant pancake.",
      "Cook for 4-5 mins per side on medium flame until deep golden brown."
    ],
    "shinchan_comment": "Crunch crunch crunch! Music to my naughty ears!"
  },
  {
    "id": "curd_bread_toast",
    "name": "Dahi Bread Toast (Curd Sandwich)",
    "time": "6 mins",
    "difficulty": "Easy",
    "ingredients": ["bread", "curd", "onion", "tomato"],
    "optional_ingredients": ["chilli"],
    "steps": [
      "Whisk thick curd with salt, black pepper, diced onions, and tomatoes.",
      "Spread the seasoned curd mixture generously between two bread slices.",
      "Toast in a pan with a smear of butter or oil until both sides are crisp.",
      "Cut diagonally and enjoy the warm creamy center!"
    ],
    "shinchan_comment": "Creamy on the inside, crunchy on the outside! Like a ninja disguise!"
  },
  {
    "id": "egg_salad_roll",
    "name": "Lazy Boiled Egg Spread & Toast",
    "time": "7 mins",
    "difficulty": "Easy",
    "ingredients": ["eggs", "bread", "onion"],
    "optional_ingredients": ["curd", "cheese"],
    "steps": [
      "Boil 2 eggs for 7 minutes, cool in water, and peel.",
      "Mash eggs roughly with a fork, pinch of salt, pepper, and finely diced onion.",
      "(Pro tip: mix in a spoon of thick curd if you have no mayo!)",
      "Spread over toasted bread slices or roll inside bread."
    ],
    "shinchan_comment": "Egg power activate! Ready to dance with beautiful older sisters!"
  },
  {
    "id": "onion_tomato_cheela",
    "name": "Quick Onion Tomato Cheela / Crêpe",
    "time": "7 mins",
    "difficulty": "Easy",
    "ingredients": ["onion", "tomato", "chilli"],
    "optional_ingredients": ["eggs", "paneer"],
    "steps": [
      "Chop onions, tomatoes, and chillies finely.",
      "Mix with flour/gram flour or whisk with 2 eggs and water to form a pourable batter.",
      "Season with salt, cumin, and red chilli powder.",
      "Pour a ladle into a greased hot pan and cook on both sides until browned."
    ],
    "shinchan_comment": "Quick flip in the pan! Wheeeee!"
  },
  {
    "id": "paneer_tikka_tawa",
    "name": "Quick Pan Paneer Bites",
    "time": "6 mins",
    "difficulty": "Easy",
    "ingredients": ["paneer", "curd", "chilli"],
    "optional_ingredients": ["onion", "tomato"],
    "steps": [
      "Cut paneer into bite-sized cubes.",
      "Toss with 1 spoon curd, red chilli powder, turmeric, and salt.",
      "Sear in a hot pan with oil for 3-4 minutes, turning sides.",
      "Serve piping hot with sliced onions on the side."
    ],
    "shinchan_comment": "Restaurant style in pajama pants! Misae would charge 500 yen for this!"
  },
  {
    "id": "banana_milkshake",
    "name": "Thick Energy Banana Shake",
    "time": "3 mins",
    "difficulty": "Super Easy",
    "ingredients": ["banana", "milk"],
    "optional_ingredients": ["curd"],
    "steps": [
      "Peel and slice 1 ripe banana into a cup or blender.",
      "Pour in 1 cup chilled milk and a pinch of sugar.",
      "Blend or mash vigorously with a fork/whisk until frothy and thick.",
      "Drink immediately for instant mischievous energy!"
    ],
    "shinchan_comment": "Gulp gulp gulp! Banana mustache mode unlocked!"
  },
  {
    "id": "spicy_boiled_egg_fry",
    "name": "Masala Boiled Egg Tawa Fry",
    "time": "6 mins",
    "difficulty": "Super Easy",
    "ingredients": ["eggs", "onion", "chilli"],
    "optional_ingredients": ["tomato"],
    "steps": [
      "Slice hard-boiled eggs in half.",
      "In a shallow pan, heat oil, throw in sliced onions and green chillies.",
      "Add turmeric, red chilli powder, and salt to create a spicy oil paste.",
      "Place egg halves cut-side down, sear for 2 mins, and baste with masala."
    ],
    "shinchan_comment": "Spicy sizzle! Even Hiroshi's beer would be jealous!"
  },
  {
    "id": "cheesy_fried_noodles",
    "name": "Creamy Cheesy Ramen Bake",
    "time": "7 mins",
    "difficulty": "Easy",
    "ingredients": ["noodles", "cheese", "milk"],
    "optional_ingredients": ["chilli", "onion"],
    "steps": [
      "Boil noodles in 1 cup of water and 1/2 cup of milk with the seasoning packet.",
      "Cook until noodles are tender and liquid reduces into a creamy gravy.",
      "Stir in chopped chilli and top with cheese slices.",
      "Turn off the heat, cover for 1 minute to let the cheese melt completely."
    ],
    "shinchan_comment": "Cheesy heaven! Goodbye diet, hello nap time!"
  },
  {
    "id": "onion_poha_rice",
    "name": "Quick Tadka Fried Rice",
    "time": "6 mins",
    "difficulty": "Easy",
    "ingredients": ["rice", "onion", "chilli"],
    "optional_ingredients": ["potato", "tomato"],
    "steps": [
      "Heat 1 tbsp oil, add mustard seeds, slit chillies, and sliced onions.",
      "Fry until onions are sweet and translucent.",
      "Add turmeric, salt, and toss in day-old cooked rice.",
      "Cover and steam for 2 minutes on low flame."
    ],
    "shinchan_comment": "Simple yellow rice that looks like sunshine! Yummy!"
  },
  {
    "id": "potato_egg_scramble",
    "name": "Spanish-Style Potato & Egg Scramble",
    "time": "8 mins",
    "difficulty": "Easy",
    "ingredients": ["potato", "eggs", "onion"],
    "optional_ingredients": ["cheese", "chilli"],
    "steps": [
      "Finely cube potato and fry in oil with sliced onion until tender and browned.",
      "Beat 2 eggs with salt and pepper.",
      "Pour eggs directly over the potatoes in the pan.",
      "Gently stir into big soft curds until eggs are just set."
    ],
    "shinchan_comment": "Eggs + potatoes = best friends forever! Like me and Kazama!"
  },
  {
    "id": "tomato_onion_salsa_toast",
    "name": "Desi Bruschetta (Spiced Tomato Toast)",
    "time": "5 mins",
    "difficulty": "Super Easy",
    "ingredients": ["bread", "tomato", "onion", "chilli"],
    "optional_ingredients": ["cheese"],
    "steps": [
      "Finely dice tomatoes and onions; toss with chillies, salt, and pepper.",
      "Toast bread slices till super crisp in butter or oil.",
      "Spoon the juicy tomato-onion mix over the toasted bread.",
      "Top with cheese shavings if available and bite into the crunch!"
    ],
    "shinchan_comment": "Fancy Italian style for Kasukabe royalty! Bellissimo!"
  },
  {
    "id": "banana_curd_sweet_bowl",
    "name": "Sweet Banana Shrikhand Bowl",
    "time": "3 mins",
    "difficulty": "Super Easy",
    "ingredients": ["banana", "curd"],
    "optional_ingredients": ["milk"],
    "steps": [
      "Whisk cold curd in a bowl with a spoon of sugar until glossy.",
      "Slice banana into rounds and gently fold into the curd.",
      "Add a pinch of cardamom or cinnamon if available in spices.",
      "Eat chilled for an instant healthy dessert."
    ],
    "shinchan_comment": "Sweet and cool! Mom can't say I didn't eat my fruits!"
  },
  {
    "id": "paneer_chilli_stirfry",
    "name": "Speedy Desi Chilli Paneer",
    "time": "8 mins",
    "difficulty": "Easy",
    "ingredients": ["paneer", "onion", "chilli", "tomato"],
    "optional_ingredients": ["green pepper"],
    "steps": [
      "Cut paneer into cubes and onions into thick petals.",
      "Sear paneer in a hot pan for 2 mins, set aside.",
      "Toss onions and chillies on high flame for a charred aroma.",
      "Add tomato ketchup or purée, splash of water, toss paneer back in and glaze."
    ],
    "shinchan_comment": "Fire in the mouth! Need water! Quick!"
  },
  {
    "id": "egg_noodle_stirfry",
    "name": "Street Hakka Egg Noodles",
    "time": "7 mins",
    "difficulty": "Easy",
    "ingredients": ["noodles", "eggs", "onion", "chilli"],
    "optional_ingredients": ["tomato"],
    "steps": [
      "Boil and drain noodles, rinsing with cold water.",
      "Scramble 1 egg in oil, remove onto a plate.",
      "Stir-fry sliced onions and chilli on high flame.",
      "Add noodles, seasoning, scrambled egg, and toss dynamically."
    ],
    "shinchan_comment": "Tossing noodles like a pro chef! Don't drop them on Shiro!"
  },
  {
    "id": "aloo_sandwich",
    "name": "Mumbai Aloo Masala Toast",
    "time": "7 mins",
    "difficulty": "Easy",
    "ingredients": ["bread", "potato", "onion", "chilli"],
    "optional_ingredients": ["cheese"],
    "steps": [
      "Mash boiled potato with chopped onion, chilli, salt, and turmeric.",
      "Spread the aloo mixture generously onto bread slices.",
      "Assemble sandwich, smear butter/oil on both outer sides.",
      "Grill on tawa until both sides are reddish-gold and extra crispy."
    ],
    "shinchan_comment": "Ultimate carb-on-carb delight! Gives me power to escape evening study!"
  },
  {
    "id": "creamy_curd_pasta_noodles",
    "name": "White-Sauce Style Curd Noodles",
    "time": "6 mins",
    "difficulty": "Easy",
    "ingredients": ["noodles", "curd", "onion"],
    "optional_ingredients": ["cheese", "chilli"],
    "steps": [
      "Boil noodles till al dente and drain.",
      "Whisk curd with salt, black pepper, and 2 tbsp warm water.",
      "Sauté onions in butter or oil, turn off the flame.",
      "Toss hot noodles with the whisked curd sauce and cheese until velvety."
    ],
    "shinchan_comment": "Creamy pasta hack! No fancy cream needed!"
  },
  {
    "id": "tomato_egg_drop_rice",
    "name": "Chinese Tomato Egg Over Rice",
    "time": "8 mins",
    "difficulty": "Easy",
    "ingredients": ["rice", "tomato", "eggs", "onion"],
    "optional_ingredients": ["chilli"],
    "steps": [
      "Scramble 2 eggs softly and remove from pan.",
      "Cook diced tomatoes with chopped onion and salt until saucy and jammy.",
      "Stir the soft eggs back into the hot tomato gravy for 30 seconds.",
      "Ladle the luscious tomato egg sauce over warm steamed rice."
    ],
    "shinchan_comment": "Classic comfort food! So juicy and delicious!"
  },
  {
    "id": "spicy_potato_bites",
    "name": "Crispy Chilli Aloo Pops",
    "time": "9 mins",
    "difficulty": "Easy",
    "ingredients": ["potato", "chilli", "onion"],
    "optional_ingredients": ["cheese"],
    "steps": [
      "Parboil or microwave potato cubes until 80% tender.",
      "In hot oil, sear potatoes until a crisp outer skin forms.",
      "Toss with finely diced onions, green chillies, salt, and chilli flakes.",
      "Finish with a squeeze of lemon or pinch of chaat masala."
    ],
    "shinchan_comment": "Pop one, pop two, oops the whole bowl is empty!"
  },
  {
    "id": "banana_egg_custard",
    "name": "Mug Banana Pudding / Custard",
    "time": "4 mins",
    "difficulty": "Super Easy",
    "ingredients": ["banana", "eggs", "milk"],
    "optional_ingredients": ["cheese"],
    "steps": [
      "Mash 1 banana with 1 egg and 2 tablespoons of milk inside a microwave-safe mug.",
      "Add a teaspoon of sugar and whisk well with a fork.",
      "Microwave for 90 seconds until puffed up and set like custard.",
      "Let cool for 1 minute before digging in."
    ],
    "shinchan_comment": "Warm banana cake in a mug! Perfect snack before television!"
  },
  {
    "id": "hated_piman_curry",
    "name": "Misae's Revenge Green Pepper Stirfry",
    "time": "8 mins",
    "difficulty": "Easy",
    "ingredients": ["green pepper", "onion", "potato"],
    "optional_ingredients": ["tomato", "paneer"],
    "steps": [
      "Chop onions, potatoes, and... groan... the green peppers.",
      "Sauté onions and potatoes in oil until potato is halfway cooked.",
      "Toss in the green peppers with turmeric, chilli powder, and salt.",
      "Cover and cook until softened, pretending it's actually delicious."
    ],
    "shinchan_comment": "BLEEEHH! Why did you pick green pepper?! Shiro, come eat this for me!"
  },
  {
    "id": "eggplant_masala",
    "name": "Shinchan's Grumpy Eggplant Roast",
    "time": "9 mins",
    "difficulty": "Easy",
    "ingredients": ["eggplant", "onion", "tomato"],
    "optional_ingredients": ["chilli"],
    "steps": [
      "Slice eggplant into discs and onions into strips.",
      "Shallow fry eggplant discs in hot oil with salt and turmeric until tender.",
      "Add sliced onions and tomatoes; cook down into a thick coating.",
      "Serve while crying dramatic anime tears."
    ],
    "shinchan_comment": "EGGPLANT?! Even Kazama wouldn't eat this! Who made this decision?!"
  }
];
let allRecipes = EMBEDDED_RECIPES;
let selectedIngredients = new Set();
let customIngredients = new Set();
let currentMatches = [];
let currentMatchIndex = 0;
let isSpinning = false;
let spinInterval = null;

// TheMealDB Integration & Cache
const THEMEALDB_MAP = {
  'eggs': 'Eggs',
  'egg': 'Eggs',
  'onion': 'Onion',
  'bread': 'Bread',
  'rice': 'Rice',
  'tomato': 'Tomato',
  'potato': 'Potatoes',
  'cheese': 'Cheese',
  'milk': 'Milk',
  'curd': 'Yogurt',
  'paneer': 'Paneer',
  'noodles': 'Noodles',
  'chilli': 'Chilli',
  'banana': 'Banana',
  'green pepper': 'Green Pepper',
  'eggplant': 'Aubergine',
  'garlic': 'Garlic',
  'butter': 'Butter'
};

const mealCache = new Map();
let kitchenMode = 'local'; // 'local' or 'world'

// Mascot Mood Controller (4 moods: happy, hungry, angry, celebrating)
function setMascotMood(mood) {
  const avatar = document.getElementById('misae-avatar');
  if (!avatar) return;
  avatar.classList.remove('mood-happy', 'mood-hungry', 'mood-angry', 'mood-celebrating');
  avatar.classList.add(`mood-${mood}`);
}

// Comic Sound Popups
const COMIC_WORDS = ["POW!", "BOING!", "BURI BURI!", "SLURP!", "CRUNCH!", "ACTION!"];

function triggerComicPopup(x, y, word) {
  const layer = document.getElementById('comic-popups-layer');
  if (!layer) return;

  const text = word || COMIC_WORDS[Math.floor(Math.random() * COMIC_WORDS.length)];
  const el = document.createElement('div');
  el.className = 'comic-word-popup';
  el.textContent = text;

  const posX = (typeof x === 'number' && !isNaN(x)) ? Math.max(20, Math.min(window.innerWidth - 120, x - 40)) : (window.innerWidth / 2 - 40);
  const posY = (typeof y === 'number' && !isNaN(y)) ? Math.max(40, y - 40) : (window.innerHeight / 2 - 40);

  el.style.left = `${posX}px`;
  el.style.top = `${posY}px`;
  layer.appendChild(el);

  setTimeout(() => {
    if (el.parentNode) el.parentNode.removeChild(el);
  }, 850);
}

// Confetti Rain (Chocobi boxes, stars, and food emojis)
function triggerConfetti() {
  const canvas = document.getElementById('confetti-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  const confettiItems = ['🍫', '🍪', '⭐', '🥟', '🍙', '🍳', '✨'];
  const particles = [];
  for (let i = 0; i < 35; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: -20 - Math.random() * 200,
      size: 20 + Math.random() * 16,
      char: confettiItems[Math.floor(Math.random() * confettiItems.length)],
      speedY: 3 + Math.random() * 4,
      speedX: (Math.random() - 0.5) * 3,
      rotation: Math.random() * 360,
      rotSpeed: (Math.random() - 0.5) * 6
    });
  }

  const startTime = Date.now();
  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => {
      p.y += p.speedY;
      p.x += p.speedX;
      p.rotation += p.rotSpeed;

      ctx.save();
      ctx.translate(p.x, p.y);
      ctx.rotate((p.rotation * Math.PI) / 180);
      ctx.font = `${p.size}px sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(p.char, 0, 0);
      ctx.restore();
    });

    if (Date.now() - startTime < 2600) {
      requestAnimationFrame(animate);
    } else {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
  }
  requestAnimationFrame(animate);
}

// DOM Elements
const chipsContainer = document.getElementById('chips-container');
const selectedCountEl = document.getElementById('selected-count');
const btnClear = document.getElementById('btn-clear');
const customForm = document.getElementById('custom-ingredient-form');
const customInput = document.getElementById('custom-input');
const btnCook = document.getElementById('btn-cook');
const misaeSpeech = document.getElementById('misae-speech');
const misaeAvatar = document.getElementById('misae-avatar');
const flashOverlay = document.getElementById('angry-flash-overlay');

const btnModeLocal = document.getElementById('btn-mode-local');
const btnModeWorld = document.getElementById('btn-mode-world');

const rouletteContainer = document.getElementById('roulette-container');
const slotReelText = document.getElementById('slot-reel-text');

const recipeDisplay = document.getElementById('recipe-display');
const cardTitle = document.getElementById('card-recipe-title');
const cardTime = document.getElementById('card-recipe-time');
const cardDiff = document.getElementById('card-recipe-diff');
const cardMatch = document.getElementById('card-recipe-match');
const cardSource = document.getElementById('card-recipe-source');
const cardImageWrap = document.getElementById('card-image-wrap');
const cardRecipeImage = document.getElementById('card-recipe-image');
const cardButtDance = document.getElementById('card-butt-dance');
const cardGrumpy = document.getElementById('card-grumpy-banner');
const grumpyText = document.getElementById('grumpy-text');
const cardSwapBox = document.getElementById('card-swap-box');
const cardSwapList = document.getElementById('card-swap-list');
const cardIngList = document.getElementById('card-ingredients-list');
const cardStepsList = document.getElementById('card-steps-list');
const cardQuote = document.getElementById('card-shinchan-quote');
const btnSpinAgain = document.getElementById('btn-spin-again');
const btnChangeIngredients = document.getElementById('btn-change-ingredients');

const fallbackDisplay = document.getElementById('fallback-display');
const fallbackMsg = document.getElementById('fallback-message');
const btnFallbackRetry = document.getElementById('btn-fallback-retry');

// Landing Screen & Intro Animation
let introTimers = [];

function clearIntroTimers() {
  introTimers.forEach(t => clearTimeout(t));
  introTimers = [];
}

function transitionToApp() {
  clearIntroTimers();
  const landingScreen = document.getElementById('landing-screen');
  const appScreen = document.getElementById('app-screen');
  if (!landingScreen || !appScreen) return;

  landingScreen.classList.add('screen-fade-out');
  setTimeout(() => {
    landingScreen.style.display = 'none';
    appScreen.style.display = 'flex';
    appScreen.classList.add('screen-fade-in');
  }, 320);
}

function initIntroScreen() {
  const landingScreen = document.getElementById('landing-screen');
  if (!landingScreen) return;

  const msg1 = document.getElementById('msg-1');
  const msg2 = document.getElementById('msg-2');
  const msg3 = document.getElementById('msg-3');
  const msgTyping = document.getElementById('msg-typing');
  const msg4 = document.getElementById('msg-4');
  const notif = document.getElementById('phone-notif');
  const btnOpenFridge = document.getElementById('btn-open-fridge');
  const btnSkip = document.getElementById('btn-skip-intro');

  // Skip button click
  if (btnSkip) {
    btnSkip.addEventListener('click', () => {
      playSound('pop');
      transitionToApp();
    });
  }

  // Open fridge CTA click
  if (btnOpenFridge) {
    btnOpenFridge.addEventListener('click', () => {
      playSound('fanfare');
      transitionToApp();
    });
  }

  // Sequence: finishes in ~6.5 seconds total (< 8 seconds)
  introTimers.push(setTimeout(() => {
    if (msg1) {
      msg1.classList.remove('hidden');
      msg1.classList.add('pop-in');
      playSound('pop');
    }
  }, 500));

  introTimers.push(setTimeout(() => {
    if (msg2) {
      msg2.classList.remove('hidden');
      msg2.classList.add('pop-in');
      playSound('pop');
    }
  }, 1800));

  introTimers.push(setTimeout(() => {
    if (msg3) {
      msg3.classList.remove('hidden');
      msg3.classList.add('pop-in');
      playSound('pop');
    }
  }, 3200));

  introTimers.push(setTimeout(() => {
    if (notif) notif.classList.add('show');
    if (msgTyping) {
      msgTyping.classList.remove('hidden');
      msgTyping.classList.add('pop-in');
    }
  }, 4400));

  introTimers.push(setTimeout(() => {
    if (msgTyping) msgTyping.classList.add('hidden');
    if (msg4) {
      msg4.classList.remove('hidden');
      msg4.classList.add('pop-in');
      playSound('pop');
    }
  }, 5800));

  introTimers.push(setTimeout(() => {
    if (btnOpenFridge) {
      btnOpenFridge.classList.remove('hidden');
      btnOpenFridge.classList.add('pop-in');
      playSound('pop');
    }
  }, 6500));
}

// Initialize
async function init() {
  initIntroScreen();
  renderChips();
  attachEvents();
  await loadRecipes();
}

// Load recipes.json
async function loadRecipes() {
  try {
    const res = await fetch('recipes.json');
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    allRecipes = await res.json();
  } catch (err) {
    console.error('Could not load recipes:', err);
    misaeSpeech.textContent = "Mama! Someone stole the recipe notebook! (Failed loading recipes.json)";
  }
}

// Check if an ingredient name is considered hated
function isHated(name) {
  const norm = name.toLowerCase().trim();
  return HATED_INGREDIENTS.some(hated => norm.includes(hated) || hated.includes(norm));
}

// Trigger Angry Shinchan tantrum (Screen shake, red flash, angry bubble)
function triggerAngryShinchan(ingredientName) {
  playSound('angry');
  // Screen shake
  document.body.classList.remove('angry-shake');
  void document.body.offsetWidth; // Force reflow
  document.body.classList.add('angry-shake');
  setTimeout(() => document.body.classList.remove('angry-shake'), 700);

  // Red flash overlay
  flashOverlay.classList.remove('active');
  void flashOverlay.offsetWidth;
  flashOverlay.classList.add('active');
  setTimeout(() => flashOverlay.classList.remove('active'), 1000);

  // Avatar and Speech
  setMascotMood('angry');
  misaeSpeech.classList.add('angry');

  const norm = ingredientName.toLowerCase();
  let quote;
  if (norm.includes('eggplant') || norm.includes('brinjal')) {
    quote = QUIPS.hatedEggplant[Math.floor(Math.random() * QUIPS.hatedEggplant.length)];
  } else {
    quote = QUIPS.hatedGreenPepper[Math.floor(Math.random() * QUIPS.hatedGreenPepper.length)];
  }

  misaeSpeech.textContent = quote;

  setTimeout(() => {
    const stillHasHated = Array.from(selectedIngredients).some(i => isHated(i));
    if (!stillHasHated) {
      if (selectedIngredients.size >= 2) setMascotMood('hungry');
      else setMascotMood('happy');
    }
  }, 4000);
}

// Update Misae speech bubble based on active selections
function updateSpeechBubble(lastSelected, wasAdded) {
  if (selectedIngredients.size === 0) {
    misaeSpeech.classList.remove('angry');
    misaeSpeech.textContent = "Mama, I'm hungry! What do we have in the fridge?";
    return;
  }

  // Check if any hated ingredient is currently in selections
  const hatedItem = Array.from(selectedIngredients).find(item => isHated(item));
  if (hatedItem && wasAdded && isHated(lastSelected)) {
    // Already triggered via triggerAngryShinchan
    return;
  }

  if (hatedItem) {
    misaeSpeech.classList.add('angry');
    misaeSpeech.textContent = `Shinchan is sulking because '${hatedItem}' is on the counter...`;
    return;
  }

  misaeSpeech.classList.remove('angry');

  // Check specific ingredient quip
  if (lastSelected && wasAdded && QUIPS.specific[lastSelected.toLowerCase()]) {
    misaeSpeech.textContent = QUIPS.specific[lastSelected.toLowerCase()];
    return;
  }

  // Pick random quip based on selection size
  if (selectedIngredients.size >= 6) {
    misaeSpeech.textContent = "Whoa, look at Gordon Ramsay over here raiding the whole kitchen!";
  } else {
    const randomQuip = QUIPS.general[Math.floor(Math.random() * QUIPS.general.length)];
    misaeSpeech.textContent = randomQuip;
  }
}

// Render chips into the grid
function renderChips() {
  chipsContainer.innerHTML = '';

  // Render default chips
  DEFAULT_CHIPS.forEach(chip => {
    const isSelected = selectedIngredients.has(chip.name);
    const hatedClass = isHated(chip.name) ? 'hated' : '';
    const chipEl = document.createElement('div');
    chipEl.className = `chip ${isSelected ? 'selected' : ''} ${hatedClass}`;
    chipEl.dataset.name = chip.name;
    chipEl.innerHTML = `<span>${chip.emoji}</span><span>${chip.label}</span>`;
    chipEl.addEventListener('click', (e) => toggleIngredient(chip.name, e));
    chipsContainer.appendChild(chipEl);
  });

  // Render custom chips
  customIngredients.forEach(name => {
    const isSelected = selectedIngredients.has(name);
    const hatedClass = isHated(name) ? 'hated' : '';
    const chipEl = document.createElement('div');
    chipEl.className = `chip ${isSelected ? 'selected' : ''} ${hatedClass}`;
    chipEl.dataset.name = name;
    chipEl.innerHTML = `
      <span>⭐</span>
      <span>${name}</span>
      <span class="chip-custom-delete" title="Remove custom ingredient">✕</span>
    `;
    
    chipEl.addEventListener('click', (e) => {
      if (e.target.classList.contains('chip-custom-delete')) {
        e.stopPropagation();
        removeCustomIngredient(name);
      } else {
        toggleIngredient(name, e);
      }
    });
    chipsContainer.appendChild(chipEl);
  });

  updateSelectedCount();
}

function updateSelectedCount() {
  const count = selectedIngredients.size;
  selectedCountEl.textContent = `${count} picked`;
}

// Toggle an ingredient on/off
function toggleIngredient(name, event) {
  let wasAdded = false;
  if (selectedIngredients.has(name)) {
    selectedIngredients.delete(name);
  } else {
    selectedIngredients.add(name);
    wasAdded = true;
    if (isHated(name)) {
      triggerAngryShinchan(name);
    } else {
      playSound('pop');
      if (selectedIngredients.size >= 2) {
        setMascotMood('hungry');
      } else {
        setMascotMood('happy');
      }
    }
  }

  if (event && typeof event.clientX === 'number') {
    triggerComicPopup(event.clientX, event.clientY);
  }

  renderChips();
  updateSpeechBubble(name, wasAdded);
}

// Add custom ingredient
function addCustomIngredient() {
  const val = customInput.value.trim().toLowerCase();
  if (!val) return;

  if (!customIngredients.has(val) && !DEFAULT_CHIPS.some(c => c.name === val)) {
    customIngredients.add(val);
  }
  selectedIngredients.add(val);
  customInput.value = '';

  if (isHated(val)) {
    triggerAngryShinchan(val);
  } else {
    updateSpeechBubble(val, true);
  }

  renderChips();
}

function removeCustomIngredient(name) {
  customIngredients.delete(name);
  selectedIngredients.delete(name);
  renderChips();
  updateSpeechBubble(name, false);
}

// Clear all
function clearSelections() {
  if (spinInterval) {
    clearInterval(spinInterval);
    spinInterval = null;
  }
  isSpinning = false;
  btnCook.disabled = false;
  selectedIngredients.clear();
  setMascotMood('happy');
  renderChips();
  recipeDisplay.classList.remove('active');
  fallbackDisplay.classList.remove('active');
  rouletteContainer.classList.remove('spinning');
  updateSpeechBubble(null, false);
}

/**
 * Smart Swaps Rules
 * ONLY suggest substitutes using ingredients the user DID pick!
 * Never tell the user to buy anything.
 */
function findSmartSwaps(recipe, userItems) {
  const swaps = [];
  const recipeIngs = recipe.ingredients.map(i => i.toLowerCase());

  // Rule 1: Missing Milk -> User has curd (+ water from pantry)
  if (recipeIngs.includes('milk') && !userItems.has('milk')) {
    if (userItems.has('curd')) {
      swaps.push({
        forItem: 'milk',
        replacement: 'curd + water',
        tip: "No milk? Whisk a spoonful of curd with a little pantry water to make smooth buttermilk substitute!"
      });
    }
  }

  // Rule 2: Missing Paneer -> User has cheese OR potato OR eggs
  if (recipeIngs.includes('paneer') && !userItems.has('paneer')) {
    if (userItems.has('cheese')) {
      swaps.push({
        forItem: 'paneer',
        replacement: 'cheese',
        tip: "No paneer? Melt in your cheese cubes for an ultra-gooey, rich upgrade!"
      });
    } else if (userItems.has('potato')) {
      swaps.push({
        forItem: 'paneer',
        replacement: 'potato',
        tip: "No paneer? Golden pan-fried potato cubes give the exact same comforting bite!"
      });
    } else if (userItems.has('eggs')) {
      swaps.push({
        forItem: 'paneer',
        replacement: 'eggs',
        tip: "No paneer? Scramble your eggs straight into the masala!"
      });
    }
  }

  // Rule 3: Missing Curd -> User has milk
  if (recipeIngs.includes('curd') && !userItems.has('curd')) {
    if (userItems.has('milk')) {
      swaps.push({
        forItem: 'curd',
        replacement: 'milk',
        tip: "No curd? Stir in warm milk with a pinch of salt to get that creamy richness!"
      });
    }
  }

  // Rule 4: Missing Bread -> User has rice
  if (recipeIngs.includes('bread') && !userItems.has('bread')) {
    if (userItems.has('rice')) {
      swaps.push({
        forItem: 'bread',
        replacement: 'rice',
        tip: "No bread? Pour this flavorful topping directly over your cooked rice!"
      });
    }
  }

  // Rule 5: Missing Rice -> User has bread OR noodles
  if (recipeIngs.includes('rice') && !userItems.has('rice')) {
    if (userItems.has('bread')) {
      swaps.push({
        forItem: 'rice',
        replacement: 'bread',
        tip: "No rice? Toast your bread and spoon this masala mixture right on top!"
      });
    } else if (userItems.has('noodles')) {
      swaps.push({
        forItem: 'rice',
        replacement: 'noodles',
        tip: "No rice? Boil your noodles and toss them straight into the sauce!"
      });
    }
  }

  // Rule 6: Missing Tomato -> User has curd
  if (recipeIngs.includes('tomato') && !userItems.has('tomato')) {
    if (userItems.has('curd')) {
      swaps.push({
        forItem: 'tomato',
        replacement: 'curd',
        tip: "No tomato? A tablespoon of tangy curd brings the same acidic punch and creaminess!"
      });
    }
  }

  // Rule 7: Missing Potato -> User has paneer
  if (recipeIngs.includes('potato') && !userItems.has('potato')) {
    if (userItems.has('paneer')) {
      swaps.push({
        forItem: 'potato',
        replacement: 'paneer',
        tip: "No potato? Cube your paneer into the dish instead for instant protein!"
      });
    }
  }

  return swaps;
}

/**
 * Matching and Ranking Engine
 */
function rankRecipes() {
  const userItems = new Set(Array.from(selectedIngredients).map(i => i.toLowerCase().trim()));
  const scored = [];

  allRecipes.forEach(recipe => {
    const coreIngs = recipe.ingredients.map(i => i.toLowerCase().trim());
    const optIngs = (recipe.optional_ingredients || []).map(i => i.toLowerCase().trim());

    let matchCount = 0;
    const matchedList = [];
    const missingList = [];

    // Check core ingredients
    coreIngs.forEach(ing => {
      // Direct match or partial match
      const hasDirect = Array.from(userItems).some(u => u.includes(ing) || ing.includes(u));
      if (hasDirect) {
        matchCount++;
        matchedList.push(ing);
      } else {
        missingList.push(ing);
      }
    });

    // Check optional ingredients for slight bonus
    let optMatchCount = 0;
    optIngs.forEach(opt => {
      if (Array.from(userItems).some(u => u.includes(opt) || opt.includes(u))) {
        optMatchCount += 0.5;
      }
    });

    // Smart swaps available for this recipe using user's items
    const swaps = findSmartSwaps(recipe, userItems);

    // If a swap exists for a missing ingredient, effectively treat it as covered
    const effectiveMatchCount = matchCount + (swaps.length * 0.9);

    // Penalty if recipe explicitly uses hated ingredient and user DID NOT pick it
    const recipeHasHated = coreIngs.some(ing => isHated(ing));
    const userPickedHated = Array.from(userItems).some(u => isHated(u));
    let penalty = 0;
    if (recipeHasHated && !userPickedHated) {
      penalty = 10; // Don't recommend hated recipe unless user specifically picked it
    }

    const totalScore = (effectiveMatchCount * 3) + optMatchCount - penalty;

    // Only consider recipes that match at least 1 ingredient or have valid swaps
    if (matchCount > 0 || (swaps.length > 0 && totalScore > 0)) {
      scored.push({
        recipe,
        matchCount,
        effectiveMatchCount,
        totalScore,
        matchedList,
        missingList,
        swaps
      });
    }
  });

  // Sort descending by totalScore, then matchCount, then shortest cooking time
  scored.sort((a, b) => {
    if (b.totalScore !== a.totalScore) return b.totalScore - a.totalScore;
    if (b.matchCount !== a.matchCount) return b.matchCount - a.matchCount;
    return parseInt(a.recipe.time) - parseInt(b.recipe.time);
  });

  return scored;
}

/**
 * TheMealDB Integration: Multi-ingredient intersection fetcher
 */
async function fetchWorldKitchenMeals(userSelectedList) {
  const mappedIngs = [];
  userSelectedList.forEach(raw => {
    const key = raw.toLowerCase().trim();
    if (THEMEALDB_MAP[key]) {
      mappedIngs.push(THEMEALDB_MAP[key]);
    } else {
      mappedIngs.push(raw.trim());
    }
  });

  if (mappedIngs.length === 0) return null;

  // 5-second timeout using AbortController
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 5000);

  try {
    const mealCounts = new Map(); // idMeal -> { idMeal, strMeal, strMealThumb, count }

    // Query filter.php once per mapped ingredient concurrently
    const promises = mappedIngs.map(async (ing) => {
      try {
        const url = `https://www.themealdb.com/api/json/v1/1/filter.php?i=${encodeURIComponent(ing)}`;
        const res = await fetch(url, { signal: controller.signal });
        if (!res.ok) return;
        const data = await res.json();
        const meals = (data && Array.isArray(data.meals)) ? data.meals : [];
        meals.forEach(m => {
          if (!m || !m.idMeal) return;
          if (mealCounts.has(m.idMeal)) {
            mealCounts.get(m.idMeal).count++;
          } else {
            mealCounts.set(m.idMeal, {
              idMeal: m.idMeal,
              strMeal: m.strMeal,
              strMealThumb: m.strMealThumb,
              count: 1
            });
          }
        });
      } catch (e) {
        // Safe null handling for failed / aborted calls
      }
    });

    await Promise.all(promises);
    clearTimeout(timeoutId);

    if (mealCounts.size === 0) return null;

    // Rank meals by frequency count descending
    const ranked = Array.from(mealCounts.values()).sort((a, b) => b.count - a.count);
    const topCandidates = ranked.slice(0, 6);

    // Lookup top candidate recipes in parallel (check in-memory cache first)
    const lookupPromises = topCandidates.map(async (cand) => {
      if (mealCache.has(cand.idMeal)) {
        return mealCache.get(cand.idMeal);
      }
      try {
        const detailUrl = `https://www.themealdb.com/api/json/v1/1/lookup.php?i=${cand.idMeal}`;
        const detailRes = await fetch(detailUrl, { signal: controller.signal });
        if (detailRes.ok) {
          const detailData = await detailRes.json();
          if (detailData && Array.isArray(detailData.meals) && detailData.meals[0]) {
            const rawMeal = detailData.meals[0];
            const parsedIngredients = [];
            for (let i = 1; i <= 20; i++) {
              const ingName = rawMeal[`strIngredient${i}`];
              if (ingName && ingName.trim()) {
                parsedIngredients.push(ingName.trim().toLowerCase());
              }
            }

            const rawSteps = (rawMeal.strInstructions || '')
              .split(/\r?\n+/)
              .map(s => s.trim())
              .filter(s => s.length > 10);
            const steps = rawSteps.length > 0 ? rawSteps.slice(0, 5) : [rawMeal.strInstructions.trim()];

            const parsedRecipe = {
              id: `world_${rawMeal.idMeal}`,
              name: rawMeal.strMeal,
              time: "15 mins",
              difficulty: rawMeal.strArea ? `${rawMeal.strArea} Special` : "World Recipe",
              ingredients: parsedIngredients.slice(0, 6),
              optional_ingredients: parsedIngredients.slice(6, 10),
              steps: steps,
              shinchan_comment: `World Kitchen discovery: ${rawMeal.strMeal}! Action Kamen would approve!`,
              source: "world",
              image: rawMeal.strMealThumb,
              matchCount: cand.count
            };

            mealCache.set(cand.idMeal, parsedRecipe);
            return parsedRecipe;
          }
        }
      } catch (e) {
        // Continue gracefully
      }
      return null;
    });

    const detailedMeals = (await Promise.all(lookupPromises)).filter(Boolean);
    return detailedMeals.length > 0 ? detailedMeals : null;
  } catch (err) {
    clearTimeout(timeoutId);
    return null;
  }
}

/**
 * Roulette Spin Animation (1.5 seconds)
 */
async function cookSomething(event) {
  if (isSpinning) return;

  if (event && typeof event.clientX === 'number') {
    triggerComicPopup(event.clientX, event.clientY);
  } else {
    triggerComicPopup();
  }

  // Case 0: No ingredients picked
  if (selectedIngredients.size === 0) {
    recipeDisplay.classList.remove('active');
    fallbackDisplay.classList.add('active');
    fallbackMsg.textContent = "You haven't picked anything! Shinchan can't cook on thin air, even with Action Bastard's help!";
    misaeSpeech.classList.remove('angry');
    misaeSpeech.textContent = "Mama! The fridge is completely empty! Are we ordering pizza?!";
    setMascotMood('hungry');
    return;
  }

  let scoredMatches = [];

  // Check if World Kitchen toggle is enabled
  if (kitchenMode === 'world') {
    btnCook.disabled = true;
    isSpinning = true;
    recipeDisplay.classList.remove('active');
    fallbackDisplay.classList.remove('active');
    rouletteContainer.classList.add('spinning');
    slotReelText.textContent = "Mummy is cooking...";

    const worldMatches = await fetchWorldKitchenMeals(Array.from(selectedIngredients));
    if (worldMatches && worldMatches.length > 0) {
      scoredMatches = worldMatches.map(m => ({
        recipe: m,
        matchCount: m.matchCount || 1,
        effectiveMatchCount: m.matchCount || 1,
        totalScore: (m.matchCount || 1) * 3,
        matchedList: m.ingredients,
        missingList: [],
        swaps: []
      }));
    } else {
      // Silently fall back to recipes.json with Misae quip
      misaeSpeech.textContent = QUIPS.offlineMisae;
      scoredMatches = rankRecipes().map(m => ({
        ...m,
        recipe: { ...m.recipe, isOfflineFallback: true }
      }));
    }
  } else {
    scoredMatches = rankRecipes();
  }

  // Case: No viable matches found
  if (scoredMatches.length === 0) {
    rouletteContainer.classList.remove('spinning');
    btnCook.disabled = false;
    isSpinning = false;
    recipeDisplay.classList.remove('active');
    fallbackDisplay.classList.add('active');
    fallbackMsg.textContent = `Even with ${Array.from(selectedIngredients).join(', ')}, Shinchan's survival cookbook is baffled! Try adding eggs, bread, noodles, or rice!`;
    misaeSpeech.textContent = "Hmm... that's a weird combo! Shiro wouldn't even smell that!";
    setMascotMood('hungry');
    return;
  }

  // Matches found: start 1.5s roulette spin
  currentMatches = scoredMatches;
  currentMatchIndex = 0;
  if (spinInterval) {
    clearInterval(spinInterval);
    spinInterval = null;
  }
  isSpinning = true;

  btnCook.disabled = true;
  recipeDisplay.classList.remove('active');
  fallbackDisplay.classList.remove('active');
  rouletteContainer.classList.add('spinning');

  // Reel through random recipe names
  const reelTitles = currentMatches.map(m => m.recipe.name);
  const startTime = Date.now();
  const spinDuration = 1500; // ~1.5s as specified

  spinInterval = setInterval(() => {
    const elapsed = Date.now() - startTime;
    const randomTitle = reelTitles[Math.floor(Math.random() * reelTitles.length)] || "Mummy is cooking...";
    slotReelText.textContent = randomTitle;
    playSound('tick');

    if (elapsed >= spinDuration) {
      clearInterval(spinInterval);
      spinInterval = null;
      rouletteContainer.classList.remove('spinning');
      btnCook.disabled = false;
      isSpinning = false;
      playSound('fanfare');
      displayRecipe(currentMatches[currentMatchIndex]);
    }
  }, 80);
}

/**
 * Display the chosen recipe card
 */
function displayRecipe(matchData) {
  const { recipe, matchCount, matchedList, missingList, swaps } = matchData;
  const userItems = new Set(Array.from(selectedIngredients).map(i => i.toLowerCase().trim()));

  // Populate title & badges
  cardTitle.textContent = recipe.name;
  cardTime.textContent = `⏱️ ${recipe.time}`;
  cardDiff.textContent = `⚡ ${recipe.difficulty}`;
  cardMatch.textContent = `🎯 ${matchCount} of ${recipe.ingredients.length} matched`;

  // Kitchen Source badge
  if (cardSource) {
    if (recipe.source === 'world') {
      cardSource.textContent = '🌍 World Kitchen';
      cardSource.className = 'badge-tag badge-source badge-world';
    } else {
      cardSource.textContent = '🏠 Local Kitchen';
      cardSource.className = 'badge-tag badge-source badge-local';
    }
  }

  // Dish photo if available
  if (cardImageWrap && cardRecipeImage) {
    if (recipe.image) {
      cardImageWrap.style.display = 'block';
      cardRecipeImage.src = recipe.image;
    } else {
      cardImageWrap.style.display = 'none';
    }
  }

  // Butt-dance celebration
  if (cardButtDance) {
    cardButtDance.style.display = 'flex';
  }

  // Confetti rain
  triggerConfetti();

  // Mascot celebratory mood
  const pickedHated = Array.from(selectedIngredients).filter(i => isHated(i));
  if (pickedHated.length > 0) {
    setMascotMood('angry');
    cardGrumpy.style.display = 'flex';
    grumpyText.textContent = `Shinchan is eating with tears in his eyes because you picked: ${pickedHated.join(', ')}! Misae made him do it!`;
  } else {
    setMascotMood('celebrating');
    cardGrumpy.style.display = 'none';
  }

  // Smart Swaps box
  if (swaps && swaps.length > 0) {
    cardSwapBox.style.display = 'flex';
    cardSwapList.innerHTML = '';
    swaps.forEach(s => {
      const li = document.createElement('li');
      li.textContent = s.tip;
      cardSwapList.appendChild(li);
    });
  } else {
    cardSwapBox.style.display = 'none';
  }

  // Ingredients checklist
  cardIngList.innerHTML = '';
  const swappedForItems = (swaps || []).map(s => s.forItem.toLowerCase());

  recipe.ingredients.forEach(ing => {
    const ingNorm = ing.toLowerCase();
    const hasIt = Array.from(userItems).some(u => u.includes(ingNorm) || ingNorm.includes(u));
    const isSwapped = swappedForItems.includes(ingNorm);
    const badge = document.createElement('span');

    if (hasIt) {
      badge.className = 'ing-badge has-it';
      badge.innerHTML = `✓ ${ing}`;
    } else if (isSwapped) {
      const matchingSwap = swaps.find(s => s.forItem.toLowerCase() === ingNorm);
      badge.className = 'ing-badge swapped';
      badge.innerHTML = `✨ ${ing} (Use ${matchingSwap.replacement})`;
    } else {
      badge.className = 'ing-badge missing';
      badge.innerHTML = `✗ ${ing}`;
    }
    cardIngList.appendChild(badge);
  });

  // Optional ingredients
  if (recipe.optional_ingredients && recipe.optional_ingredients.length > 0) {
    recipe.optional_ingredients.forEach(opt => {
      const optNorm = opt.toLowerCase();
      const hasIt = Array.from(userItems).some(u => u.includes(optNorm) || optNorm.includes(u));
      const badge = document.createElement('span');
      if (hasIt) {
        badge.className = 'ing-badge has-it';
        badge.innerHTML = `✓ ${opt} (Bonus)`;
      } else {
        badge.className = 'ing-badge missing';
        badge.innerHTML = `+ ${opt} (Optional)`;
      }
      cardIngList.appendChild(badge);
    });
  }

  // Steps
  cardStepsList.innerHTML = '';
  recipe.steps.forEach(step => {
    const li = document.createElement('li');
    li.textContent = step;
    cardStepsList.appendChild(li);
  });

  // Shinchan Quote
  cardQuote.textContent = `"${recipe.shinchan_comment || 'Action Bastard approved survival food!'}"`;

  // Update Misae speech bubble
  if (recipe.isOfflineFallback) {
    misaeSpeech.classList.remove('angry');
    misaeSpeech.textContent = QUIPS.offlineMisae;
  } else if (pickedHated.length > 0) {
    misaeSpeech.classList.add('angry');
    misaeSpeech.textContent = `BLEEEHH! Shinchan is forced to eat ${recipe.name}! Misae, save me!`;
  } else {
    misaeSpeech.classList.remove('angry');
    misaeSpeech.textContent = `Look what Shinchan made! '${recipe.name}'! Dig in before Shiro steals it!`;
  }

  // Show card
  recipeDisplay.classList.add('active');

  // Smooth scroll into view
  recipeDisplay.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Spin Again button (Next best match)
 */
function spinAgain() {
  if (currentMatches.length <= 1) {
    misaeSpeech.textContent = "That's the absolute best match we have for these ingredients!";
    return;
  }

  // Next index
  currentMatchIndex = (currentMatchIndex + 1) % currentMatches.length;

  // Quick 400ms mini-spin flair
  const match = currentMatches[currentMatchIndex];
  recipeDisplay.classList.remove('active');
  rouletteContainer.classList.add('spinning');
  slotReelText.textContent = match.recipe.name;

  setTimeout(() => {
    rouletteContainer.classList.remove('spinning');
    displayRecipe(match);
  }, 400);
}

// Attach Event Listeners
function attachEvents() {
  // Add custom ingredient form
  customForm.addEventListener('submit', (e) => {
    e.preventDefault();
    addCustomIngredient();
  });

  // Sound toggle button
  const soundToggleBtn = document.getElementById('btn-sound-toggle');
  const soundIcon = document.getElementById('sound-icon');
  if (soundToggleBtn && soundIcon) {
    soundToggleBtn.addEventListener('click', (e) => {
      soundEnabled = !soundEnabled;
      soundIcon.textContent = soundEnabled ? '🔊' : '🔇';
      if (soundEnabled) {
        playSound('pop');
        triggerComicPopup(e.clientX, e.clientY, "AUDIO ON!");
      } else {
        triggerComicPopup(e.clientX, e.clientY, "MUTED!");
      }
    });
  }

  // Kitchen Mode Selection (Local vs World)
  const btnLocal = document.getElementById('btn-mode-local');
  const btnWorld = document.getElementById('btn-mode-world');
  if (btnLocal && btnWorld) {
    btnLocal.addEventListener('click', (e) => {
      kitchenMode = 'local';
      btnLocal.classList.add('active');
      btnWorld.classList.remove('active');
      playSound('pop');
      triggerComicPopup(e.clientX, e.clientY, "DESI TADKA!");
      misaeSpeech.textContent = "Local survival kitchen active! Mummy ke secret desi nuskhe!";
    });

    btnWorld.addEventListener('click', (e) => {
      kitchenMode = 'world';
      btnWorld.classList.add('active');
      btnLocal.classList.remove('active');
      playSound('pop');
      triggerComicPopup(e.clientX, e.clientY, "WORLD TOUR!");
      misaeSpeech.textContent = "World Kitchen active! Foreign recipes with desi tadka!";
    });
  }

  // Clear button
  btnClear.addEventListener('click', (e) => {
    triggerComicPopup(e.clientX, e.clientY, "CLEARED!");
    clearSelections();
  });

  // Cook button
  btnCook.addEventListener('click', cookSomething);

  // Spin again
  btnSpinAgain.addEventListener('click', (e) => {
    triggerComicPopup(e.clientX, e.clientY, "SPINNING!");
    spinAgain();
  });

  // Copy recipe to clipboard
  const btnCopy = document.getElementById('btn-copy-recipe');
  const copyText = document.getElementById('copy-text');
  if (btnCopy && copyText) {
    btnCopy.addEventListener('click', () => {
      const match = currentMatches[currentMatchIndex];
      if (!match) return;
      const r = match.recipe;
      const text = [
        `🍳 ${r.name} (${r.time} • ${r.difficulty})`,
        `🛒 Ingredients: ${r.ingredients.join(', ')}`,
        `🔥 Steps:`,
        ...r.steps.map((s, i) => `${i + 1}. ${s}`),
        `\n"${r.shinchan_comment || 'Action Bastard approved!'}"`
      ].join('\n');

      navigator.clipboard.writeText(text).then(() => {
        copyText.textContent = 'Copied!';
        playSound('pop');
        setTimeout(() => { copyText.textContent = 'Copy Recipe'; }, 2000);
      }).catch(() => {
        copyText.textContent = 'Done!';
        setTimeout(() => { copyText.textContent = 'Copy Recipe'; }, 2000);
      });
    });
  }

  // Edit ingredients (scroll back up)
  btnChangeIngredients.addEventListener('click', () => {
    document.getElementById('ingredients-panel').scrollIntoView({ behavior: 'smooth' });
  });

  // Fallback retry button
  btnFallbackRetry.addEventListener('click', () => {
    fallbackDisplay.classList.remove('active');
    document.getElementById('ingredients-panel').scrollIntoView({ behavior: 'smooth' });
  });
}

// Kick off when DOM is ready
document.addEventListener('DOMContentLoaded', init);
