import { apiRequest } from "../config/api";

export function fetchAccessUsers() {
  return apiRequest("/access/users");
}

export function createAccessUser(payload) {
  return apiRequest("/access/users", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateAccessUser(userId, payload) {
  return apiRequest(`/access/users/${userId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function fetchRoles() {
  return apiRequest("/access/roles");
}

export function createRole(payload) {
  return apiRequest("/access/roles", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateRole(roleId, payload) {
  return apiRequest(`/access/roles/${roleId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function fetchPermissions() {
  return apiRequest("/access/permissions");
}

export function fetchBranches() {
  return apiRequest("/access/branches");
}

export function createBranch(payload) {
  return apiRequest("/access/branches", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateBranch(branchId, payload) {
  return apiRequest(`/access/branches/${branchId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function fetchVendors(includeInactive = false) {
  const suffix = includeInactive ? "?include_inactive=true" : "";
  return apiRequest(`/access/vendors${suffix}`);
}

export function createVendor(payload) {
  return apiRequest("/access/vendors", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateVendor(vendorId, payload) {
  return apiRequest(`/access/vendors/${vendorId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function createAccessProfile(payload) {
  return apiRequest("/access/profiles", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateAccessProfile(profileId, payload) {
  return apiRequest(`/access/profiles/${profileId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}
