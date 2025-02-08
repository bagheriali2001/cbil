<script>
	import { selectedFeatures } from '$lib/store/store.js';
	import { createEventDispatcher } from 'svelte';
	const dispatch = createEventDispatcher();

	let items = [
		{ name: 'Color Mean', id: 'mean' },
		{ name: 'Color Histogram', id: 'hist' },
		{ name: 'GLCM', id: 'glcm' },
		{ name: 'HOG', id: 'hog' },
		{ name: 'GIST', id: 'gist' },
		{ name: 'DCT', id: 'dct' },
		{ name: 'Wavelet', id: 'wavelet' },
		{ name: 'Harris Corners', id: 'corners' }
	];
	export let isOpen = false;

	let pre_selected = [''];

	function toggleSelection(item) {
		selectedFeatures.update((current) => {
			if (current.includes(item)) {
				return current.filter((i) => i !== item);
			} else {
				return [...current, item];
			}
		});
	}

	function closeSidebar() {
		dispatch('toggleSidebar');
	}
</script>

<div class="sidebar {isOpen ? 'open' : ''}">
	<h3>Select Items</h3>

	<div class="item-list">
		{#each items as item}
			<div
				class="item {$selectedFeatures.includes(item.id) ? 'selected' : ''}"
				on:click={() => toggleSelection(item.id)}
			>
				{item.name}
			</div>
		{/each}
	</div>

	<div class="button-group">
		<button class="confirm-btn" on:click={closeSidebar}>Confirm</button>
		<button class="reset-btn" on:click={() => selectedFeatures.set([])}>Reset</button>
	</div>
</div>

<style>
	.sidebar {
		position: fixed;
		top: 0;
		right: 0;
		width: 320px;
		height: 100%;
		background: #070707;
		box-shadow: -2px 0 10px rgba(255, 165, 0, 0.3);
		transform: translateX(100%);
		transition: transform 0.3s ease-in-out;
		padding: 20px;
		display: flex;
		flex-direction: column;
		justify-content: space-between;
		border-left: 2px solid #e17f00;
		z-index: 900;
	}

	.sidebar.open {
		transform: translateX(0);
	}

	.sidebar h3 {
		color: #e17f00;
		text-align: center;
	}

	.item-list {
		flex-grow: 1;
		overflow-y: auto;
		margin-top: 15px;
		padding-right: 5px;
	}

	.item {
		padding: 12px;
		cursor: pointer;
		border-bottom: 1px solid #222;
		background-color: #111;
		color: #aaaaaa;
		transition: background 0.3s ease;
		border-radius: 5px;
		margin: 5px 0;
		text-align: center;
	}

	.item:hover {
		background: #222221;
	}

	.item.selected {
		background: #e17f00;
		color: white;
	}

	.close-btn {
		position: absolute;
		top: 10px;
		right: 10px;
		background: red;
		color: white;
		border: none;
		padding: 8px 12px;
		cursor: pointer;
		border-radius: 5px;
		transition: background 0.3s ease;
	}

	.close-btn:hover {
		background: darkred;
	}

	.button-group {
		display: flex;
		gap: 10px;
		justify-content: center;
		padding: 10px 0;
	}

	.confirm-btn,
	.reset-btn {
		padding: 10px 20px;
		font-size: 16px;
		border-radius: 5px;
		cursor: pointer;
		transition: background-color 0.3s ease;
		border: none;
		color: #ffffff;
	}

	.confirm-btn {
		background-color: #e17f00;
	}

	.confirm-btn:hover {
		background-color: #d67500;
	}

	.reset-btn {
		background-color: #444444;
	}

	.reset-btn:hover {
		background-color: #333333;
	}
</style>
