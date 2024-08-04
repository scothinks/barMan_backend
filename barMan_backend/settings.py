// src/contexts/__tests__/InventoryContext.test.js

import React from 'react';
import { renderHook, act } from '@testing-library/react-native';
import { InventoryProvider, useInventory } from '../InventoryContext';
import * as api from '../../services/api';

// Mock the API functions
jest.mock('../../services/api', () => ({
  getInventoryItems: jest.fn(),
  createInventoryItem: jest.fn(),
  updateInventoryItem: jest.fn(),
  deleteInventoryItem: jest.fn(),
  confirmDeleteInventoryItem: jest.fn(),
  restoreInventoryItem: jest.fn(),
}));

// Mock the AuthContext
jest.mock('../AuthContext', () => ({
  useAuth: () => ({
    logout: jest.fn(),
    isAuthenticated: jest.fn(() => true),
  }),
}));

describe('InventoryContext', () => {
  const wrapper = ({ children }) => <InventoryProvider>{children}</InventoryProvider>;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('provides initial inventory state', () => {
    const { result } = renderHook(() => useInventory(), { wrapper });

    expect(result.current.inventoryItems).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('fetches inventory items', async () => {
    const mockItems = [
      { id: 1, name: 'Item 1', cost: '10.50', is_deleted: false },
      { id: 2, name: 'Item 2', cost: 20, is_deleted: 'false' },
    ];
    api.getInventoryItems.mockResolvedValueOnce(mockItems);

    const { result } = renderHook(() => useInventory(), { wrapper });

    await act(async () => {
      result.current.fetchInventoryItems();
      // Add a small delay to allow for state updates
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.inventoryItems).toEqual([
      { id: 1, name: 'Item 1', cost: 10.50, is_deleted: false },
      { id: 2, name: 'Item 2', cost: 20, is_deleted: false },
    ]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('adds an inventory item', async () => {
    const newItem = { name: 'New Item', cost: '30.00' };
    const addedItem = { id: 3, ...newItem, cost: 30 };
    api.createInventoryItem.mockResolvedValueOnce(addedItem);

    const { result } = renderHook(() => useInventory(), { wrapper });

    await act(async () => {
      await result.current.addInventoryItem(newItem);
    });

    expect(result.current.inventoryItems).toContainEqual(addedItem);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('updates an inventory item', async () => {
    const updatedItem = { id: 1, name: 'Updated Item', cost: 40 };
    api.updateInventoryItem.mockResolvedValueOnce(updatedItem);

    const { result } = renderHook(() => useInventory(), { wrapper });

    await act(async () => {
      await result.current.updateInventoryItem(1, updatedItem);
    });

    expect(result.current.inventoryItems).toContainEqual(updatedItem);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('deletes an inventory item', async () => {
    api.deleteInventoryItem.mockResolvedValueOnce({});

    const { result } = renderHook(() => useInventory(), { wrapper });

    // Add an item to delete
    result.current.inventoryItems = [{ id: 1, name: 'Item to delete', is_deleted: false }];

    await act(async () => {
      await result.current.deleteInventoryItem(1);
    });

    expect(result.current.inventoryItems[0].is_deleted).toBe(true);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('confirms deletion of an inventory item', async () => {
    api.confirmDeleteInventoryItem.mockResolvedValueOnce({});

    const { result } = renderHook(() => useInventory(), { wrapper });

    // Add an item to confirm delete
    result.current.inventoryItems = [{ id: 1, name: 'Item to confirm delete' }];

    await act(async () => {
      await result.current.confirmDeleteInventoryItem(1);
    });

    expect(result.current.inventoryItems).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('restores a deleted inventory item', async () => {
    const restoredItem = { id: 1, name: 'Restored Item', cost: 50, is_deleted: false };
    api.restoreInventoryItem.mockResolvedValueOnce(restoredItem);

    const { result } = renderHook(() => useInventory(), { wrapper });

    // Add a deleted item to restore
    result.current.inventoryItems = [{ id: 1, name: 'Deleted Item', is_deleted: true }];

    await act(async () => {
      await result.current.restoreInventoryItem(1);
    });

    expect(result.current.inventoryItems).toContainEqual(restoredItem);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('handles errors when fetching inventory items', async () => {
    api.getInventoryItems.mockRejectedValueOnce(new Error('Fetch error'));

    const { result } = renderHook(() => useInventory(), { wrapper });

    await act(async () => {
      result.current.fetchInventoryItems();
      // Add a small delay to allow for state updates
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.error).toBe('Failed to fetch inventory items. Please try again.');
    expect(result.current.isLoading).toBe(false);
  });

  it('refreshes inventory', async () => {
    const mockItems = [{ id: 1, name: 'Refreshed Item', cost: '60.00', is_deleted: false }];
    api.getInventoryItems.mockResolvedValueOnce(mockItems);

    const { result } = renderHook(() => useInventory(), { wrapper });

    await act(async () => {
      result.current.refreshInventory();
      // Add a small delay to allow for state updates
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.inventoryItems).toEqual([
      { id: 1, name: 'Refreshed Item', cost: 60, is_deleted: false },
    ]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });
});