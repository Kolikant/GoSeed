// CPP code to check if a key is present 
// in an unordered_map 
#include <bits/stdc++.h> 
using namespace std; 

// Function to check if the key is present or not 
string check_key(unordered_map<string, int> m, string key) 
{ 
	// Key is not present 
	if (m.find(key) == m.end()) 
		return "Not Present"; 

	return "Present"; 
} 

// Driver 
int main() 
{ 
	unordered_map<string, int> m; 

	// Initialising keys and mapped values 
	m["1"] = 4; 
	m["2"] = 6; 
	m["4"] = 6; 

	// Keys to be checked 
	string check1 = "5", check2 = "4"; 

	// Function call 
	cout << check1 << ": " << check_key(m, check1) << '\n'; 
	cout << check2 << ": " << check_key(m, check2); 
} 
