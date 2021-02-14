from hashlib import sha256

def main():
	print("Please input")
	print("\nSHA-256:\n" + sha256(input().encode()).hexdigest())

main()
