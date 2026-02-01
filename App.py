"""Cloudflare DDNS Updater - GUI Application."""

import math
from tkinter import messagebox
import tkinter

import customtkinter

import server


class App(customtkinter.CTk):
    """Main application window for DDNS updater."""
    
    FONT_STYLE = ("Helvetica", 15)
    PADDING = {"padx": 10, "pady": 10}
    
    def __init__(self):
        super().__init__()
        self._init_window()
        self._init_state()
        self._load_credentials_or_prompt()
    
    def _init_window(self):
        """Configure initial window settings."""
        self.title("Dynamic DNS Updater")
        self.geometry("700x255")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure((0, 1), weight=1)
    
    def _init_state(self):
        """Initialize application state variables."""
        self.api_email = ""
        self.api_key = ""
        self.name_list = []
        self.checkboxes = []
        self.zone_id_dict = {}
        self.dns_records = {}
        self.checkboxes_dns = []
        self.selected_dns_names = []
    
    def _load_credentials_or_prompt(self):
        """Try loading saved credentials, otherwise show input form."""
        config = server.load_config()
        if config:
            self.api_email = config.get("api_email", "")
            self.api_key = config.get("api_key", "")
            self.name_list = server.get_domains(self.api_email, self.api_key)
            
            if self.name_list:
                self._show_domain_selection()
                return
            
            messagebox.showerror(
                "Error!", 
                "Saved credentials are invalid or no domains found on account."
            )
        
        self._show_credentials_form()

    # Frame 1: Credentials Input
    def _show_credentials_form(self):
        """Display form for Cloudflare credentials input."""
        self.lbl_email = customtkinter.CTkLabel(
            self, text="Enter Cloudflare Email:", font=self.FONT_STYLE
        )
        self.lbl_email.grid(row=0, column=0, sticky="w", **self.PADDING)
        
        self.entry_email = customtkinter.CTkEntry(self, font=self.FONT_STYLE)
        self.entry_email.grid(row=0, column=1, sticky="ew", **self.PADDING)
        
        self.lbl_api_key = customtkinter.CTkLabel(
            self, text="Enter Cloudflare API Key:", font=self.FONT_STYLE
        )
        self.lbl_api_key.grid(row=1, column=0, sticky="w", **self.PADDING)
        
        self.entry_api_key = customtkinter.CTkEntry(self, font=self.FONT_STYLE, show="*")
        self.entry_api_key.grid(row=1, column=1, sticky="ew", **self.PADDING)
        
        self.lbl_key_type = customtkinter.CTkLabel(
            self, text="Select API Key Type:", font=self.FONT_STYLE
        )
        self.lbl_key_type.grid(row=2, column=0, sticky="w", **self.PADDING)
        
        self.key_type_var = tkinter.IntVar(value=1)
        
        self.radio_global = customtkinter.CTkRadioButton(
            self, text="Global API Key", variable=self.key_type_var, value=1
        )
        self.radio_global.grid(row=2, column=1, sticky="ew", **self.PADDING)
        
        self.radio_token = customtkinter.CTkRadioButton(
            self, text="API Token (DNS Access)", variable=self.key_type_var, value=2
        )
        self.radio_token.grid(row=3, column=1, sticky="ew", **self.PADDING)
        
        self.btn_submit_creds = customtkinter.CTkButton(
            self, text="Submit", font=self.FONT_STYLE, command=self._validate_credentials
        )
        self.btn_submit_creds.grid(row=4, column=0, columnspan=2, sticky="ew", **self.PADDING)
    
    def _validate_credentials(self):
        """Validate and process credential input."""
        email = self.entry_email.get().strip()
        api_key = self.entry_api_key.get().strip()
        
        if not email or not api_key:
            messagebox.showerror("Error!", "Please enter both email and API key.")
            return
        
        # Format API key based on type
        if self.key_type_var.get() == 2:
            api_key = f"Bearer {api_key}"
        
        # Test credentials by fetching domains
        domains = server.get_domains(email, api_key)
        
        if not domains:
            messagebox.showerror(
                "Error!", 
                "Invalid credentials or no domains found on account."
            )
            return
        
        self.api_email = email
        self.api_key = api_key
        self.name_list = domains
        self._clear_credentials_form()
        self._show_domain_selection()
    
    def _clear_credentials_form(self):
        """Remove credentials form widgets."""
        widgets = [
            'lbl_email', 'entry_email', 'lbl_api_key', 'entry_api_key',
            'lbl_key_type', 'radio_global', 'radio_token', 'btn_submit_creds'
        ]
        for widget_name in widgets:
            widget = getattr(self, widget_name, None)
            if widget:
                widget.destroy()

    # Frame 2: Domain Selection
    def _show_domain_selection(self):
        """Display domain selection checkboxes."""
        rows_needed = math.ceil(len(self.name_list) / 2)
        height = (rows_needed * 60) + 120
        self.geometry(f"500x{height}")
        
        self.lbl_domains = customtkinter.CTkLabel(
            self, text="Select domains to update DNS for:", font=self.FONT_STYLE
        )
        self.lbl_domains.grid(row=0, column=0, columnspan=2, sticky="ew", **self.PADDING)
        
        self.checkboxes = []
        for i, domain in enumerate(self.name_list):
            row = (i // 2) + 1
            col = i % 2
            checkbox = customtkinter.CTkCheckBox(self, text=domain, font=self.FONT_STYLE)
            checkbox.grid(row=row, column=col, sticky="w", **self.PADDING)
            self.checkboxes.append(checkbox)
        
        self.btn_submit_domains = customtkinter.CTkButton(
            self, text="Submit", font=self.FONT_STYLE, command=self._process_domain_selection
        )
        self.btn_submit_domains.grid(
            row=rows_needed + 2, column=0, columnspan=2, sticky="ew", **self.PADDING
        )
    
    def _process_domain_selection(self):
        """Process selected domains and fetch DNS records."""
        selected = [cb.cget("text") for cb in self.checkboxes if cb.get() == 1]
        
        if not selected:
            messagebox.showerror("Error!", "Please select at least one domain.")
            return
        
        # Fetch zone IDs and DNS records for selected domains
        self.zone_id_dict = {}
        self.dns_records = {}
        
        for domain in selected:
            zone_id = server.get_zone_id(self.api_email, self.api_key, domain)
            if zone_id:
                self.zone_id_dict[domain] = zone_id
                records = server.get_dns_records(self.api_email, self.api_key, zone_id)
                if records:
                    self.dns_records[zone_id] = records
        
        if not self.dns_records:
            messagebox.showerror("Error!", "No DNS records found for selected domains.")
            return
        
        self._clear_domain_selection()
        self._show_dns_selection()
    
    def _clear_domain_selection(self):
        """Remove domain selection widgets."""
        if hasattr(self, 'lbl_domains'):
            self.lbl_domains.destroy()
        if hasattr(self, 'btn_submit_domains'):
            self.btn_submit_domains.destroy()
        for checkbox in self.checkboxes:
            checkbox.destroy()
        self.checkboxes = []

    # Frame 3: DNS Record Selection
    def _show_dns_selection(self):
        """Display DNS record selection checkboxes."""
        total_records = sum(len(records) for records in self.dns_records.values())
        rows_needed = math.ceil(total_records / 2)
        height = (rows_needed * 60) + 120
        self.geometry(f"500x{height}")
        
        self.lbl_dns = customtkinter.CTkLabel(
            self, text="Select DNS records to update:", font=self.FONT_STYLE
        )
        self.lbl_dns.grid(row=0, column=0, columnspan=2, sticky="ew", **self.PADDING)
        
        self.checkboxes_dns = []
        i = 0
        for zone_id, records in self.dns_records.items():
            for record_name in records:
                row = (i // 2) + 1
                col = i % 2
                checkbox = customtkinter.CTkCheckBox(
                    self, text=record_name, font=self.FONT_STYLE
                )
                checkbox.grid(row=row, column=col, sticky="w", **self.PADDING)
                self.checkboxes_dns.append(checkbox)
                i += 1
        
        self.btn_submit_dns = customtkinter.CTkButton(
            self, text="Update DNS", font=self.FONT_STYLE, command=self._process_dns_selection
        )
        self.btn_submit_dns.grid(
            row=rows_needed + 2, column=0, columnspan=2, sticky="ew", **self.PADDING
        )
    
    def _process_dns_selection(self):
        """Process selected DNS records and perform updates."""
        self.selected_dns_names = [
            cb.cget("text") for cb in self.checkboxes_dns if cb.get() == 1
        ]
        
        if not self.selected_dns_names:
            messagebox.showerror("Error!", "Please select at least one DNS record.")
            return
        
        self._update_dns_records()
    
    def _clear_dns_selection(self):
        """Remove DNS selection widgets."""
        if hasattr(self, 'lbl_dns'):
            self.lbl_dns.destroy()
        if hasattr(self, 'btn_submit_dns'):
            self.btn_submit_dns.destroy()
        for checkbox in self.checkboxes_dns:
            checkbox.destroy()
        self.checkboxes_dns = []

    # DNS Update Logic
    def _update_dns_records(self):
        """Update selected DNS records with current IP."""
        # Save credentials
        server.update_data({
            "api_email": self.api_email,
            "api_key": self.api_key,
        })
        
        current_ip = server.get_current_ip()
        if not current_ip:
            messagebox.showerror("Error!", "Failed to detect current IP address.")
            return
        
        updates_made = 0
        updates_skipped = 0
        
        for domain, zone_id in self.zone_id_dict.items():
            if zone_id not in self.dns_records:
                continue
                
            for dns_name, dns_id in self.dns_records[zone_id].items():
                if dns_name not in self.selected_dns_names:
                    continue
                
                previous_ip = server.get_previous_ip(
                    self.api_email, self.api_key, zone_id, dns_id
                )
                
                if current_ip != previous_ip:
                    success = server.update_dns(
                        self.api_email, self.api_key, current_ip,
                        zone_id, dns_name, dns_id
                    )
                    if success:
                        updates_made += 1
                else:
                    updates_skipped += 1
        
        # Show summary
        if updates_made > 0:
            messagebox.showinfo(
                "Success!", 
                f"Updated {updates_made} DNS record(s) to {current_ip}"
            )
        elif updates_skipped > 0:
            messagebox.showinfo(
                "No Changes", 
                "IP address has not changed. No updates required."
            )
        
        self.destroy()


def main():
    """Application entry point."""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
