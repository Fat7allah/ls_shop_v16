// Copyright (c) 2026, Ls Shop and contributors
// For license information, please see license.txt

frappe.ui.form.on("Reward Redemption", {
	refresh: function(frm) {
		// Set sales person to current user if new document
		if (frm.is_new() && !frm.doc.sales_person) {
			frappe.db.get_value("Sales Person", {"user_id": frappe.session.user}, "name")
				.then(r => {
					if (r.message) {
						frm.set_value("sales_person", r.message.name);
					}
				});
		}
		
		// Add browse catalog button
		if (frm.is_new() || frm.doc.docstatus === 0) {
			frm.add_custom_button(__("Browse Catalog"), function() {
				browse_catalog(frm);
			}, __("Actions"));
		}
		
		// Update headline with balance info
		update_headline(frm);
	},

	customer: function(frm) {
		if (!frm.doc.customer) {
			frm.set_value("current_balance", 0);
			return;
		}
		
		// Fetch and display customer balance
		frappe.call({
			method: "ls_shop.reward_api.get_customer_balance",
			args: { customer: frm.doc.customer },
			callback: function(r) {
				if (r.message) {
					frm.set_value("current_balance", r.message.balance);
					update_headline(frm);
				}
			}
		});
	},

	validate: function(frm) {
		// Calculate total points from items
		let total = 0;
		(frm.doc.redemption_items || []).forEach(function(row) {
			row.total_points = (row.points_per_unit || 0) * (row.quantity || 0);
			total += row.total_points;
		});
		
		frm.set_value("total_points_used", total);
		
		// Check balance (server-side will validate again)
		if (frm.doc.current_balance && total > frm.doc.current_balance) {
			frappe.throw(
				__("Solde insuffisant. Le client dispose de {0} points mais cette rédemption nécessite {1} points.",
				[frm.doc.current_balance, total])
			);
		}
	}
});

frappe.ui.form.on("Reward Redemption Item", {
	quantity: function(frm, cdt, cdn) {
		calculate_row_total(frm, cdt, cdn);
		update_total_points(frm);
	},
	
	items_remove: function(frm) {
		update_total_points(frm);
	}
});

function calculate_row_total(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	row.total_points = (row.points_per_unit || 0) * (row.quantity || 0);
	frm.refresh_field("redemption_items");
}

function update_total_points(frm) {
	let total = 0;
	(frm.doc.redemption_items || []).forEach(function(row) {
		total += (row.total_points || 0);
	});
	frm.set_value("total_points_used", total);
	update_headline(frm);
}

function update_headline(frm) {
	if (frm.doc.current_balance !== undefined) {
		let color = "blue";
		let message = __("Solde actuel: <b>{0} pts</b>", [frm.doc.current_balance]);
		
		if (frm.doc.total_points_used) {
			if (frm.doc.total_points_used > frm.doc.current_balance) {
				color = "red";
				message = __(
					"<span style='color:red'>⚠ Solde insuffisant: {0} pts disponibles, {1} pts nécessaires</span>",
					[frm.doc.current_balance, frm.doc.total_points_used]
				);
			} else {
				let remaining = frm.doc.current_balance - frm.doc.total_points_used;
				message = __(
					"Solde: <b>{0} pts</b> | Utilisé: <b>{1} pts</b> | Restant: <b>{2} pts</b>",
					[frm.doc.current_balance, frm.doc.total_points_used, remaining]
				);
			}
		}
		
		frm.dashboard.set_headline(message);
	}
}

function browse_catalog(frm) {
	frappe.call({
		method: "ls_shop.reward_api.get_active_catalog_items",
		callback: function(r) {
			if (!r.message || r.message.length === 0) {
				frappe.msgprint(__("No active catalog items found."));
				return;
			}
			
			let catalog_items = r.message;
			
			let dialog = new frappe.ui.Dialog({
				title: __("Catalogue de récompenses"),
				size: "large",
				fields: [
					{
						fieldname: "catalog_html",
						fieldtype: "HTML"
					}
				]
			});
			
			// Build catalog HTML
			let html = '<div style="padding: 16px; display: flex; flex-wrap: wrap; gap: 16px;">';
			
			catalog_items.forEach(function(item) {
				let image_url = item.item_image || "/assets/frappe/images/no-image.png";
				html += `
					<div style="width: 180px; border: 1px solid #ddd; border-radius: 8px; padding: 12px; text-align: center;">
						<img src="${image_url}" style="width: 100px; height: 100px; object-fit: contain; margin-bottom: 8px;">
						<p style="font-weight: 500; margin: 8px 0 4px; font-size: 13px;">${item.item_name}</p>
						<p style="color: #666; font-size: 12px; margin-bottom: 8px;">${item.points_required} pts / unité</p>
						<button class="btn btn-sm btn-primary add-item-btn" 
							data-item="${item.name}"
							data-item-code="${item.item}"
							data-item-name="${item.item_name}"
							data-points="${item.points_required}">
							+ ${__("Ajouter")}
						</button>
					</div>
				`;
			});
			
			html += '</div>';
			
			dialog.fields_dict.catalog_html.html(html);
			
			// Bind click events
			dialog.$wrapper.on('click', '.add-item-btn', function() {
				let $btn = $(this);
				let catalog_item = $btn.data('item');
				let item_code = $btn.data('item-code');
				let item_name = $btn.data('item-name');
				let points = parseInt($btn.data('points'));
				
				// Add to redemption items
				let child = frm.add_child('redemption_items', {
					reward_catalog_item: catalog_item,
					item: item_code,
					item_name: item_name,
					points_per_unit: points,
					quantity: 1,
					total_points: points
				});
				
				frm.refresh_field('redemption_items');
				update_total_points(frm);
				dialog.hide();
			});
			
			dialog.show();
		}
	});
}
