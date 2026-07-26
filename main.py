import discord
import os # default module
from dotenv import load_dotenv
import math
import random
from simpleeval import simple_eval, InvalidExpression
from google import genai



load_dotenv() # load all the variables from the env file
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name="hello", description="Say hello to the bot")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond("Hey!/https://www.icegif.com/wp-content/uploads/2023/08/icegif-223.gif")

@bot.slash_command(name="ping", description="Check the bot's latency")
async def ping(ctx: discord.ApplicationContext):
    await ctx.respond(f"Pong! Latency: {round(bot.latency * 1000)} ms")

@bot.slash_command(name="bye", description="Say goodbye to the bot")
async def bye(ctx: discord.ApplicationContext):
    await ctx.respond("Goodbye! See you later!")

@bot.slash_command(name="add", description="Add two numbers")
async def add(ctx: discord.ApplicationContext, first: int, second: int):
    result = first + second
    responses = [
        f"Easy — {first} plus {second} comes out to {result}.",
        f"That's {result}. Add {first} and {second} and there you go!",
        f"{first} + {second}? That's {result}.",
    ]
    await ctx.respond(random.choice(responses))

@bot.slash_command(name="subtract", description="Subtract two numbers")
async def subtract(ctx: discord.ApplicationContext, first: int, second: int):
    result = first - second
    responses = [
        f"Take {second} away from {first} and you're left with {result}.",
        f"That works out to {result}.",
        f"{first} minus {second} is {result}.",
    ]
    await ctx.respond(random.choice(responses))

@bot.slash_command(name="thankyou", description="Thank the bot")
async def thank_you(ctx: discord.ApplicationContext):
    await ctx.respond("You're welcome!")

@bot.slash_command(name="multiply", description="Multiply two numbers")
async def multiply(ctx: discord.ApplicationContext, first: int, second: int):
    result = first * second
    responses = [
        f"{first} times {second}? That's {result}.",
        f"Multiplying those gives you {result}.",
        f"Comes out to {result}.",
    ]
    await ctx.respond(random.choice(responses))

@bot.slash_command(name="divide", description="Divide two numbers")
async def divide(ctx: discord.ApplicationContext, first: int, second: int):
    if second == 0:
        await ctx.respond("Whoa, can't divide by zero — math police would arrest me.")
        return
    result = first / second
    responses = [
        f"That's {result}.",
        f"{first} divided by {second} gives you {result}.",
        f"Dividing those out, you get {result}.",
    ]
    await ctx.respond(random.choice(responses))

@bot.slash_command(name="calculate", description="Do math with two numbers")
async def calculate(
    ctx: discord.ApplicationContext,
    first: int = discord.Option(description="First number"),
    second: int = discord.Option(description="Second number"),
    operation: str = discord.Option(
        description="Choose an operation",
        choices=["add", "subtract", "multiply", "divide"]
    )
):
    if operation == "add":
        result = first + second
        responses = [
            f"Easy — {first} plus {second} comes out to {result}.",
            f"That's {result}. Add {first} and {second} and there you go!",
            f"{first} + {second}? That's {result}.",
        ]
    elif operation == "subtract":
        result = first - second
        responses = [
            f"Take {second} away from {first} and you're left with {result}.",
            f"That works out to {result}.",
            f"{first} minus {second} is {result}.",
        ]
    elif operation == "multiply":
        result = first * second
        responses = [
            f"{first} times {second}? That's {result}.",
            f"Multiplying those gives you {result}.",
            f"Comes out to {result}.",
        ]
    elif operation == "divide":
        if second == 0:
            await ctx.respond("Whoa, can't divide by zero — math police would arrest me.")
            return
        result = round(first / second, 2)
        responses = [
            f"That's {result}.",
            f"{first} divided by {second} gives you {result}.",
            f"Dividing those out, you get {result}.",
        ]

    await ctx.respond(random.choice(responses))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith("!hello"):
        await message.channel.send("Hello there!")


@bot.slash_command(name="bedmas", description="Evaluate a math expression (respects order of operations)")
async def bedmas(ctx: discord.ApplicationContext, expression: str = discord.Option(str, "e.g. 3 + 4 * (2 - 1) or sqrt(16)")):
    expression = expression.replace("^", "**")
    try:
        result = simple_eval(expression, functions={"sqrt": math.sqrt})
        await ctx.respond(f"`{expression}` = **{result}**")
    except ZeroDivisionError:
        await ctx.respond("Whoa, can't divide by zero — math police would arrest me.")
    except (InvalidExpression, SyntaxError, ValueError):
        await ctx.respond("That doesn't look like a valid expression. Try something like `sqrt(16) + 3 * 2`.")

@bot.slash_command(name="ask", description="Ask Gemini a question")
async def ask(ctx: discord.ApplicationContext, question: discord.Option(str, "What do you want to ask?")):
    await ctx.defer()  # Gemini might take a couple seconds to respond
    response = gemini_client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=question
    )
    answer = response.text
    await ctx.respond(answer[:2000])  # Discord messages cap at 2000 characters

@bot.slash_command(name="imagine", description="Generate an image from a text prompt")
async def imagine(ctx: discord.ApplicationContext, prompt: discord.Option(str, "Describe the image you want")):
    await ctx.defer()  # image generation takes a few seconds

    response = gemini_client.models.generate_images(
        model="imagen-4.0-generate-001",
        prompt=prompt,
        config={"number_of_images": 1}
    )

    # extract image bytes safely
    try:
        image_bytes = response.generated_images[0].image.image_bytes
    except Exception:
        await ctx.respond("Failed to generate image.")
        return

    with open("generated.png", "wb") as f:
        f.write(image_bytes)

    await ctx.respond(file=discord.File("generated.png"))

bot.run(os.getenv('BOT_TOKEN')) # run the bot with the token
