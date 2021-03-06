import axios from "axios";

import constants from "./apiConstants";

class ApiRequester {
    constructor(setStatus) {
        this.setStatus = setStatus;
    }

    async addPlayer(playerName, regions) {
        try {
            const result = await axios.post(constants.addPlayerUrl, {
                player_name: playerName,
                regions: regions
            });
            return this.setResult(result)
        } catch (err) {
        }
    }

    async removePlayer(playerName) {
        try {
            const result = await axios.delete(
                `${constants.removePlayerUrl}/${playerName}`,
                {
                    name: playerName
                }
            );
            return this.setResult(result);
        } catch (err) {
        }
    }

    async addRoom(playerName, roomName, regions) {
        try {
            const result = await axios.post(constants.addRoomUrl, {
                player_name: playerName,
                room_name: roomName,
                regions: regions
            });
            return this.setResult(result);
        } catch (err) {
        }
    }

    setResult(result) {
        if (result && result.status === 200) {
            this.setStatus(result.data);
            return true;
        }
    }

    async fetchData() {
        const result = await axios.get(constants.status);
        return this.setResult(result);
    }
}

export default ApiRequester;
