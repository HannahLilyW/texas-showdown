const names = [
    'Aaron', 'Arlo', 'Atlas', 'Abraham', 'Ace', 'Alonzo', 'Ambrose', 'Amos', 'August',
    'Bartholomew', 'Benjamin', 'Bennet', 'Bill', 'Billy', 'Boone', 'Brandon', 'Buck', 'Butch',
    'Calvin', 'Carson', 'Cassidy', 'Cedar', 'Cisco', 'Clarence', 'Clint', 'Clinton', 'Cody', 'Cole', 'Colt', 'Cooper',
    'Darius', 'David', 'Duke', 'Dusty',
    'Elias', 'Elijah', 'Elroy', 'Emmett', 'Ethan', 'Ezrah',
    'Fred',
    'Gabe', 'Garrett', 'George', 'Gideon', 'Giles', 'Gunner', 'Gus',
    'Hank', 'Harrison', 'Harvey', 'Horace', 'Holt', 'Houston', 'Hunter',
    'Isaac',
    'Jack', 'James', 'Jasper', 'Jeb', 'Jed', 'Jeremiah', 'Jesse', 'Jim',
    'Kit', 'Knox',
    'Lee', 'Levi', 'Luke',
    'Marshall', 'Maxwell', 'Michah', 'Moses', 'Myles',
    'Nash',
    'Obediah', 'Owen',
    'Pablo',
    'Quinn',
    'Ranger', 'Roderick', 'Ryder',
    'Samuel', 'Seth',
    'Tex', 'Theodore', 'Travis',
    'Ulysses',
    'Vince',
    'Will', 'Wyatt',
    'Xander',
    'York',
    'Zachariah', 'Zeke',
    'Annie', 'Abigale', 'Ada', 'Amelia', 'Augusta', 'Ava',
    'Belle', 'Betsy', 'Bonnie',
    'Caroline', 'Cassie', 'Charlotte', 'Claire', 'Clementine', 'Constance', 'Cora',
    'Daisy', 'Dakota', 'Dixie', 'Delilah',
    'Edwina', 'Ella', 'Eleanor', 'Eliza', 'Ellie', 'Elsie', 'Elvira', 'Emma', 'Esther', 'Etta',
    'Frances', 'Flora',
    'Georgia', 'Grace',
    'Hannah', 'Hattie', 'Helen', 'Hope',
    'Isabel',
    'Jane', 'Jessamine', 'Joan', 'Josephine', 'Judith',
    'Katherine',
    'Lenora', 'Lily', 'Lorraine', 'Lucy', 'Lydia',
    'Mae', 'Maisie', 'Millie', 'Mary', 'Maybelle', 'Minerva', 'Myra',
    'Nelly', 'Nettie', 'Nora',
    'Pearl', 'Polly',
    'Rachel', 'Rebecca', 'Rosie', 'Rowena', 'Ruth',
    'Sadie', 'Sally', 'Sarah', 'Shirley', 'Susannah', 'Selina', 'Stella',
    'Willa', 'Winifred', 'Winona',
    'Xandra',
    'Yasmin', 'Yvette', 'Yvonne',
    'Zylphia'
]

export function randomName() {
    return names[Math.floor(Math.random()*names.length)];
}

const colors = [
    'black',
    'red',
    'blue',
    'brown',
    'green',
    'yellow',
    'purple',
    'gray',
    'white',
    'skin1',
    'skin2',
    'skin3',
    'skin4',
    'blank'
]

export function randomColor() {
    return colors[Math.floor(Math.random()*colors.length)];
}
