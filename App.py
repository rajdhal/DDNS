from tkinter import messagebox
import tkinter
import customtkinter
import server
import math
import json

class App(customtkinter.CTk):
    font_style = ("Helvetica", 15)
    
    # Check for stored credentials to bypass Frame 1
    def frame1(self):
        # Attempt to access stored credentials
        try:
            with open("config.json", "r") as f:
                data = json.load(f)
                self.api_email = data["api_email"]
                self.api_key = data["api_key"]
                # Obtain available domain names on account
                self.name_list = server.get_domains(self.api_email, self.api_key)
            
                # If no domains were found, suggest possible errors
                if self.name_list is None:
                    messagebox.showerror("Error!", "Credentials or Key Type were Invalid, or no domain names are on the account!")
                    self.frame1_options()
                self.frame2() 
                
        # If not found, move to frame that asks user to input them 
        except FileNotFoundError:
            self.frame1_options()
    
    # Display UI for User Input of Cloudflare Credentials   
    def frame1_options(self):
        # Title
        self.title_1 = customtkinter.CTkLabel(self, text="Enter Cloudflare Email:", font=App.font_style)
        self.title_1.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # User input textbox
        self.textbox_1 = customtkinter.CTkEntry(self, font=App.font_style)
        self.textbox_1.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Title
        self.title_2 = customtkinter.CTkLabel(self, text="Enter Cloudflare API Key:", font=App.font_style)
        self.title_2.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        # User input textbox
        self.textbox_2 = customtkinter.CTkEntry(self, font=App.font_style)
        self.textbox_2.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # Title for radio options
        self.title_radio = customtkinter.CTkLabel(self, text="Select Cloudflare API Key Type:", font=App.font_style)
        self.title_radio.grid(row=3, column=0, padx=10, pady=10, sticky="w", rowspan=2)
        
        # Two radio options for key type
        self.radio_keyType = tkinter.IntVar(value=1)
        
        self.radiobutton_global = customtkinter.CTkRadioButton(self, text="Global API Key", variable=self.radio_keyType, value=1)
        self.radiobutton_global.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        
        self.radiobutton_token = customtkinter.CTkRadioButton(self, text="Token API Key with Access to DNS Records", variable=self.radio_keyType, value=2)
        self.radiobutton_token.grid(row=4, column=1, padx=10, pady=10, sticky="ew")
        
        # Submit Button
        self.button_1 = customtkinter.CTkButton(self, text="Submit", font=App.font_style, command=lambda: self.checkFrame1())
        self.button_1.grid(row=5, column=0, padx=10, pady=10, sticky="ew", columnspan=2)
    
    # Check input of Frame 1 for errors
    def checkFrame1(self):
        # Obtain user inputted credentials
        self.api_email = self.textbox_1.get().strip()
        self.api_key = self.textbox_2.get().strip()
        
        # Check if obtained values are not empty
        if not self.api_key or not self.api_email:
            messagebox.showerror("Error!", "Please Enter Your Credentials to Continue")
            self.clearFrame1()
            self.frame1_options()
        else:
            # If the key is a token, append "Bearer" to it
            # TODO: Implement global key functionalities
            if (self.radio_keyType.get() == 2): self.api_key = f"Bearer {self.api_key}"
            self.clearFrame1()
            
            # Obtain available domain names on account
            self.name_list = server.get_domains(self.api_email, self.api_key)
            
            # If no domains were found, suggest possible errors
            if self.name_list is None:
                messagebox.showerror("Error!", "Credentials or Key Type were Invalid, or no domain names are on the account!")
                self.frame1_options()
            else:
                # Move to second frame
                self.frame2()
        
    # Destroy all entities of frame 1
    def clearFrame1(self):
        self.title_radio.destroy()
        self.radiobutton_global.destroy()
        self.radiobutton_token.destroy()
        
        self.title_1.destroy()
        self.title_2.destroy()
        self.textbox_1.destroy()
        self.textbox_2.destroy()
        self.button_1.destroy()
    
    # Display UI to choose which domain names to update DNS records for
    def frame2(self):
        # Adjust height of window to account for number of domains that can be selected
        height = ((math.ceil(len(self.name_list) / 2)) * 60) + 120 # each new row of 2 should add 60 pixels to the height
        self.geometry(f"500x{height}")
        
        # Title
        self.title_3 = customtkinter.CTkLabel(self, text="Please select the domains you would like to update the DNS for", font=App.font_style)
        self.title_3.grid(row=0, column=0, padx=10, pady=10, sticky="ew", columnspan=2)
        
        # Create correct number of checkboxes, one for each domain obtained from account
        self.checkboxes = []
        for i, value in enumerate(self.name_list, start=1):
            checkbox = customtkinter.CTkCheckBox(self, text=value, font=App.font_style)
            checkbox.grid(row=math.ceil(i/2), column=not(i%2), padx=10, pady=10, sticky="w") # 2 per row, 1 in each column
            self.checkboxes.append(checkbox)
        
        # Submit Button 
        self.button_2 = customtkinter.CTkButton(self, text="Submit", font=App.font_style, command=lambda: self.checkFrame2())
        self.button_2.grid(row=(len(self.name_list)+2), column=0, padx=10, pady=10, sticky="ew", columnspan=2)
    
    # Check input of Frame 2 for errors
    def checkFrame2(self):
        # Create list of selected domain names
        self.checked_domain_names = []
        for checkbox in self.checkboxes:
            if checkbox.get() == 1:
                self.checked_domain_names.append(checkbox.cget("text"))
        
        # If no domain names were selected, error, clear, go back
        if len(self.checked_domain_names) == 0:
            messagebox.showerror("Error!", "Please Select a Domain Name to Continue")
            self.clearFrame2()
            self.frame2()
        else:
            # Obtain zone IDs for each domain selected
            # {Domain Name: Zone ID}
            # TODO: remove need for list, or for dictionary
            self.zone_id_dict = {}
            self.zone_id_list = []
            for domain_name in self.checked_domain_names:
                self.zone_id_dict[domain_name] = server.get_zone_id(self.api_email, self.api_key, domain_name)
                self.zone_id_list.append(self.zone_id_dict[domain_name])
            
            # Obtain DNS IDs for each zone ID obtained - should segment based off of zone ID
            # {ZONE ID: {DNS RECORD NAME: DNS ID}}
            self.DNS_ids = {}
            for zone_id in self.zone_id_list:
                self.DNS_ids[zone_id] = server.get_dns_id(self.api_email, self.api_key, zone_id)
            
            # If no Zone IDs were found, or no DNS records were found
            # TODO: seperate error checks, and if no DNS records were found, offer to create one
            if self.zone_id_list is None or self.DNS_ids is None:
                messagebox.showerror("Error!", "Domain Name Selected has no Valid DNS Records!")
                self.clearFrame2()
                self.frame2()
            else:
                self.clearFrame2()
                self.frame3()   
    
    # Destroy all entities from Frame 2  
    def clearFrame2(self):
        self.title_3.destroy()
        self.button_2.destroy()
        for checkbox in self.checkboxes:
            checkbox.destroy()
    
    # Display UI to choose which DNS Records to update         
    def frame3(self):
        # Adjust height of window to account for number of DNS records that can be selected
        height = ((math.ceil(len(self.DNS_ids) / 2)) * 60) + 120
        self.geometry(f"500x{height}")
        
        # Title
        self.title_4 = customtkinter.CTkLabel(self, text="Please select which DNS records you would like to update", font=App.font_style)
        self.title_4.grid(row=0, column=0, padx=10, pady=10, sticky="ew", columnspan=2)
        
        # Create checkboxes for each DNS record found 
        self.checkboxes_DNS = []
        for zone_id in self.zone_id_list:
            for i, value in enumerate(self.DNS_ids[zone_id], start=1):
                checkbox = customtkinter.CTkCheckBox(self, text=value, font=App.font_style)
                checkbox.grid(row=math.ceil(i/2), column=not(i%2), padx=10, pady=10, sticky="w") # 2 per row, 1 in each column
                self.checkboxes_DNS.append(checkbox)
        
        # Submit Button
        self.button_2 = customtkinter.CTkButton(self, text="Submit", font=App.font_style, command=lambda: self.checkFrame3())
        self.button_2.grid(row=(len(self.checkboxes_DNS)+2), column=0, padx=10, pady=10, sticky="ew", columnspan=2)
    
    # Check input of Frame 3 for errors
    def checkFrame3(self):
        # Create list of selected DNS Records
        self.checked_checkboxes_DNS = []
        for checkbox in self.checkboxes_DNS:
            if checkbox.get() == 1:
                self.checked_checkboxes_DNS.append(checkbox.cget("text"))
        
        # If no DNS Records were selected, return
        if len(self.checked_checkboxes_DNS) == 0:
            messagebox.showerror("Error!", "Please Select a DNS Record to Continue")
            self.clearFrame3()
            self.frame3()
        else:
            self.modifyDNS()

    # Destroy all entities from Frame 3
    def clearFrame3(self):
        self.title_4.destroy()
        self.button_2.destroy()
        for checkbox in self.checkboxes_DNS:
            checkbox.destroy()

    # Update DNS record with new IP address
    def modifyDNS(self):
        # {DOMAIN NAME: ZONE ID} -> self.zone_id_dict -> all approved
        # {ZONE ID: {DNS NAME: DNS ID}} -> self.DNS_ids
        # [DNS NAMES] -> checked_checkboxes_DNS -> all approved
        
        # Obtain current ip address, and previous if available, then store credentials in dictionary
        data = {
            "api_email": self.api_email,
            "api_key": self.api_key,
        }

        # Update config.json to store the credentials
        server.update_data(data)
        
        current_ip = server.get_current_ip()
        # If the IP address that was stored no longer matches the current IP address, time to update the DNS record
        for domain_name, zone_id in self.zone_id_dict.items():
            for DNS_name in self.DNS_ids[zone_id]:
                if DNS_name in self.checked_checkboxes_DNS:
                    DNS_id = self.DNS_ids[zone_id][DNS_name]
                    previous_ip = server.get_previous_ip(self.api_email, self.api_key, zone_id, DNS_id)
                    if current_ip != previous_ip: 
                        server.update_dns(self.api_email, self.api_key, current_ip, zone_id, DNS_name, DNS_id)
                        messagebox.showinfo("Success!","Cloudflare IP address updated to " + current_ip)
                    else:
                        messagebox.showinfo("","IP address has not changed. No update required.")

        self.destroy()

    # Constructor for App
    def __init__(self):
        super().__init__()
        
        # Setup initial window settings
        self.title("Dynamic DNS Updater")
        self.geometry("700x255")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure((0, 1), weight=1)
        self.frame1()
   

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()