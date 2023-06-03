# EPL
EPL is a new interpreter programming language i've been working on, which has a tree-walk interpreter coded in python, and a bytecode interpreter which I am currently working on, in C++. EPL was originally made for the creation of a book "Creating an interpreter in python" which I worked on. EPL stands for "Easy Programming Language"

# Running EPL Files
Once you have installed the required files, you can run "main.py" with the appropriate arguments to execute the code.


If you want a normal execution, you use:
```
py main.py -i file.epl
```


If you want a normal execution with debug information, you use:
```
py main.py -i file.epl -d
```


If you want a normal execution with full debug information (including gloals), you use:
```
py main.py -i file.epl -fd
```


If you want to compile to .gof intermediate representation, you use:
```
py main.py -c file.epl
```

# EPL Syntax
Syntax in EPL is a combination of python and javascript with the intention of making a language as beginner-friendly as possible.


### Basics

```js
// Variables
var1 = 45
var2 = 32

var_res = (var1 + var2)^2
```

You can see that the differences from EPL to PRUX are the fact that we have a power operator and we don't require any initialization keywords like "let"
and we don't need semicolons either

```js
// Strings
name = "Michael"
age = 15

welcome = "Welcome, {name}! You are {age} years old and you are thus not allowed"
```

Another difference is that EPL has string interpolation and you can use "+" to concatenate multiple strings together, but the better approach is to use
the interpolation syntax. It also handles concatenation with numbers properly and doesn't error.

```js
// Data Structures
array = ["Stupard", "Michael"]
object = [
    name = array[1]
    age = 15
]

welcome = "Welcome, {object.name}! You're {object.age} years old!"
```

Arrays and objects work the same as in RUX in the background, the difference being that objects do not require any seperation like ";" or ",", but arrays do

```js
// Basic Logic
option = null

male = true
welcome = null

if !male {
    welcome = "You are a woman"
} else if option == "nonbinary" {
    welcome = "You are nonbinary"
} else {
    welcome = "You are normal"
}
```

If statements have stayed the same, one thing that changed is, that the idea of "dynamic if statements" is gone, and you have the traditional if statements.

```js
// Advanced Logic
GENDERS = [
    male = 0
    female = 1
]

name = "Chloe"
age = 15
gender = GENDERS.female

if age < 18 and name != "Michael" and gender != GENDERS.female {
    log("Underaged!")
} else if name == "Michael" or gender == GENDERS.female {
    log("Underaged but granted!")
}
```

The difference between this and RUX is that instead of "||" and "&&" I took a more beginner friendly approach with the keywords "or" and "and"

```js
// While Loops
while true {
    sleep(0.05)
    log("Hello World!")
}
```

This is a never ending loop which prints "Hello World!". (TIP: Press "CTRL+C" to exit the terminal if you run this command)

```js
// For Loops [1]
for index in 0, 100 {
    log(index)
    if index == 69 {break}
}
```

For loops have changed entirely in syntax compared to RUX. RUX has the C-Style for loops, while EPL has a very friendly approach in for loops, this one
basically going from 0 to 69.

```js
// For Loops [2]
user = [
    name = "<Mic>"
    age = 15
]

for data in user {
    log("{data.key} -> {data.value}")
}
```

A new thing in EPL is this type of for loop which works with both arrays and dictionaries, basically making "data" an object with the "key" and "value" attributes.

```js
// Lambda Functions
sqrt = (x) => x ^ (1 / 2)

log(sqrt(10))
```
```js
// Functions
base_user = [
    name = null
    age = null
    id = null
]

generate_unique_id = (user) => {
    first_bit = "{#(user.name)}:{user.age}"
    second_bit = random(1, (#(user.name) + tonumber(user.age))*10^6)

    id = "{first_bit}->{second_bit}"
    return id
}

base_user.name = "Michael"
base_user.age = 15

log(generate_unique_id(base_user))
```

A key difference in EPL is that function definitions are now seen as expressions, which allows anonymous methods by default. We also have a lambda which was shown above.
And a normal method which was shown above too. One thing you might of notices is the "#" which is the length operator which works on arrays, objects and strings.

```js
import "exEpl/user.epl"

make_user("Michael", 15)
output_user()
```

```js
// "exEpl/user.epl"

user = [
    name = null
    age = null
]

make_user = (x1, x2) => {
    user.name = x1
    user.age = x2
}

output_user = () => {
    log("This is your user:\n")
    sleep(0.5)

    log("{user.name} : {user.age}")
}
```

Compared to RUX, imports take the entire global environment of the file instead of specified items, so you don't have to explicitly "return" anything at a global level.

```js
// Globals
firstTime = time()

log("Hello World!")
tonumber("100")
tostring(100)

max = input("Input a max number: ")
rand_num = random(1, max)

log("Random number: {rand_num}")

log("Time taken: {time() - firstTime}")
```

These are all the globals in EPL and features in EPL so far, new features are coming in the language slowly.
