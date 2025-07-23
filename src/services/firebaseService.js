// src/services/firebaseService.js
import { db } from '../firebaseConfig';
import {
    collection,
    addDoc,
    arrayUnion,
    getDocs,
    doc,
    getDoc,
    setDoc,
    updateDoc,
    deleteDoc,
    query,
    where,
    serverTimestamp,
    orderBy,
    onSnapshot,
    writeBatch
} from 'firebase/firestore';

// --- Projects ---
export const createProject = async (userId, projectData) => {
    const docRef = await addDoc(collection(db, "projects"), {
        ...projectData,
        ownerId: userId,
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp(),
    });
    return docRef.id;
};

export const getProjects = async () => {
    // For now, gets all projects. Later could be filtered by membership.
    const q = query(collection(db, "projects"), orderBy("createdAt", "desc"));
    const querySnapshot = await getDocs(q);
    return querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
};

export const getProjectDetails = async (projectId) => {
    const docRef = doc(db, "projects", projectId);
    const docSnap = await getDoc(docRef);
    if (docSnap.exists()) {
        return { id: docSnap.id, ...docSnap.data() };
    } else {
        throw new Error("Project not found");
    }
};

export const updateProject = async (projectId, projectData) => {
    const projectRef = doc(db, "projects", projectId);
    await updateDoc(projectRef, {
        ...projectData,
        updatedAt: serverTimestamp(),
    });
};

export const deleteProject = async (projectId) => {
    // Note: This only deletes the project document itself. It does not cascade
    // and remove associated agents, models, or chats. Their `projectIds`
    // field will contain a reference to a now-deleted project.
    const projectRef = doc(db, "projects", projectId);
    await deleteDoc(projectRef);
};


// --- Models ---
export const createModel = async (userId, modelData) => {
    const docRef = await addDoc(collection(db, "models"), {
        ...modelData,
        ownerId: userId,
        isPublic: modelData.isPublic || false,
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp()
    });
    return docRef.id;
};

export const getMyModels = async (userId) => {
    const q = query(collection(db, "models"), where("ownerId", "==", userId), orderBy("name", "asc"));
    const querySnapshot = await getDocs(q);
    return querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
};

export const getPublicModels = async (currentUserId) => {
    const q = query(collection(db, "models"), where("isPublic", "==", true), orderBy("name", "asc"));
    const querySnapshot = await getDocs(q);
    return querySnapshot.docs
        .map(doc => ({ id: doc.id, ...doc.data() }))
        .filter(model => model.ownerId !== currentUserId);
};

export const getModelsForProjects = async (projectIds) => {
    if (!projectIds || projectIds.length === 0) return [];
    const q = query(collection(db, "models"), where("projectIds", "array-contains-any", projectIds));
    const querySnapshot = await getDocs(q);
    return querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
};


export const getModelDetails = async (modelId) => {
    const docRef = doc(db, "models", modelId);
    const docSnap = await getDoc(docRef);
    if (docSnap.exists()) {
        return { id: docSnap.id, ...docSnap.data() };
    } else {
        throw new Error("Model not found");
    }
};

export const updateModel = async (modelId, updatedData) => {
    const modelRef = doc(db, "models", modelId);
    await updateDoc(modelRef, {
        ...updatedData,
        updatedAt: serverTimestamp()
    });
};

export const deleteModel = async (modelId) => {
    await deleteDoc(doc(db, "models", modelId));
};


// --- Agents ---
export const createAgentInFirestore = async (userId, agentData, isImport = false) => {
    const dataToSave = {
        userId,
        ...agentData,
        isPublic: false,
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp(),
        deploymentStatus: "not_deployed",
        vertexAiResourceName: null,
        lastDeployedAt: null,
        lastDeploymentAttemptAt: null,
        deploymentError: null,
    };
    if (isImport) {
        delete dataToSave.id;
    }

    const docRef = await addDoc(collection(db, "agents"), dataToSave);
    return docRef.id;
};

export const getMyAgents = async (userId) => {
    const q = query(collection(db, "agents"), where("userId", "==", userId), orderBy("name", "asc"));
    const querySnapshot = await getDocs(q);
    return querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
};

export const getPublicAgents = async (currentUserId) => {
    const q = query(collection(db, "agents"), where("isPublic", "==", true), orderBy("name", "asc"));
    const querySnapshot = await getDocs(q);
    return querySnapshot.docs
        .map(doc => ({ id: doc.id, ...doc.data() }))
        .filter(agent => agent.userId !== currentUserId);
};

export const getAgentsForProjects = async (projectIds) => {
    if (!projectIds || projectIds.length === 0) return [];
    const q = query(collection(db, "agents"), where("projectIds", "array-contains-any", projectIds));
    const querySnapshot = await getDocs(q);
    return querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
}

export const getAgentDetails = async (agentId) => {
    const docRef = doc(db, "agents", agentId);
    const docSnap = await getDoc(docRef);
    if (docSnap.exists()) {
        return { id: docSnap.id, ...docSnap.data() };
    } else {
        throw new Error("Agent not found");
    }
};

export const updateAgentInFirestore = async (agentId, updatedData) => {
    const agentRef = doc(db, "agents", agentId);
    await updateDoc(agentRef, {
        ...updatedData,
        updatedAt: serverTimestamp()
    });
};

export const deleteAgentFromFirestore = async (agentId) => {
    await deleteDoc(doc(db, "agents", agentId));
};

// --- Chats ---
export const createChat = async (userId, chatData) => {
    const docRef = await addDoc(collection(db, "chats"), {
        ...chatData,
        ownerId: userId,
        createdAt: serverTimestamp(),
        lastInteractedAt: serverTimestamp(),
    });
    return docRef.id;
};

export const getChatsForProjects = async (projectIds) => {
    if (!projectIds || projectIds.length === 0) return [];
    const q = query(collection(db, "chats"), where("projectIds", "array-contains-any", projectIds), orderBy("lastInteractedAt", "desc"));
    const querySnapshot = await getDocs(q);
    return querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
};

export const getChatDetails = async (chatId) => {
    const docRef = doc(db, "chats", chatId);
    const docSnap = await getDoc(docRef);
    if (docSnap.exists()) {
        return { id: docSnap.id, ...docSnap.data() };
    } else {
        throw new Error("Chat not found");
    }
};

export const updateChat = async (chatId, chatData) => {
    const chatRef = doc(db, "chats", chatId);
    await updateDoc(chatRef, {
        ...chatData,
        updatedAt: serverTimestamp(),
    });
};

export const deleteChat = async (chatId) => {
    const chatRef = doc(db, "chats", chatId);
    const messagesRef = collection(db, "chats", chatId, "messages");

    const batch = writeBatch(db);

    // Get all messages and add delete operations to the batch
    const messagesSnapshot = await getDocs(messagesRef);
    messagesSnapshot.forEach((messageDoc) => {
        batch.delete(messageDoc.ref);
    });

    // Add the chat document delete operation to the batch
    batch.delete(chatRef);

    // Commit the batch
    await batch.commit();
};

export const addChatMessage = async (chatId, messageData) => {
    const chatRef = doc(db, "chats", chatId);
    const messagesColRef = collection(chatRef, "messages");

    const batch = writeBatch(db);

    // Add new message
    const newMessageRef = doc(messagesColRef);
    batch.set(newMessageRef, {
        ...messageData,
        childMessageIds: [], // Always initialize with empty children
        timestamp: serverTimestamp(),
    });

    // Update parent message's children array, if applicable
    if (messageData.parentMessageId) {
        const parentMessageRef = doc(messagesColRef, messageData.parentMessageId);
        batch.update(parentMessageRef, {
            childMessageIds: arrayUnion(newMessageRef.id)
        });
    }

    // Update chat's lastInteractedAt timestamp
    batch.update(chatRef, { lastInteractedAt: serverTimestamp() });

    await batch.commit();
    return newMessageRef.id;
};

export const getChatMessages = async (chatId) => {
    const q = query(collection(db, "chats", chatId, "messages"), orderBy("timestamp", "asc"));
    const querySnapshot = await getDocs(q);
    return querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
};

export const listenToChatMessages = (chatId, onUpdate) => {
    const q = query(collection(db, "chats", chatId, "messages"), orderBy("timestamp", "asc"));
    const unsubscribe = onSnapshot(q, (querySnapshot) => {
        const messages = querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
        onUpdate(messages);
    }, (error) => {
        console.error(`Error listening to chat messages for chat ${chatId}:`, error);
        onUpdate([], error);
    });
    return unsubscribe;
};

export const updateChatMessage = async (chatId, messageId, dataToUpdate) => {
    const messageRef = doc(db, "chats", chatId, "messages", messageId);
    await updateDoc(messageRef, dataToUpdate);
}


// --- Agent Runs (Legacy) ---
export const getAgentRuns = async (agentId) => {
    const q = query(collection(db, "agents", agentId, "runs"), orderBy("timestamp", "desc"));
    const querySnapshot = await getDocs(q);
    return querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
};

export const listenToAgentRun = (agentId, runId, onUpdate) => {
    const runRef = doc(db, "agents", agentId, "runs", runId);
    const unsubscribe = onSnapshot(runRef, (docSnap) => {
        if (docSnap.exists()) {
            onUpdate({ id: docSnap.id, ...docSnap.data() });
        } else {
            onUpdate(null, new Error("Run document not found."));
        }
    }, (error) => {
        onUpdate(null, error);
    });
    return unsubscribe;
};


// --- User Profile and Permissions ---
export const ensureUserProfile = async (authUser) => {
    if (!authUser) return null;
    const userRef = doc(db, "users", authUser.uid);
    const userSnap = await getDoc(userRef);

    if (userSnap.exists()) {
        await updateDoc(userRef, {
            lastLoginAt: serverTimestamp(),
            email: authUser.email,
            displayName: authUser.displayName || null,
            photoURL: authUser.photoURL || null,
        });
        return { uid: userSnap.id, ...userSnap.data() };
    } else {
        const newUserProfile = {
            uid: authUser.uid,
            email: authUser.email,
            displayName: authUser.displayName || null,
            photoURL: authUser.photoURL || null,
            createdAt: serverTimestamp(),
            lastLoginAt: serverTimestamp(),
        };
        await setDoc(userRef, newUserProfile);
        return newUserProfile;
    }
};

export const getUsersForAdminReview = async () => {
    const usersCol = collection(db, "users");
    const userSnapshot = await getDocs(usersCol);
    const allUsers = userSnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    return allUsers.filter(user => user.permissions === undefined);
};

export const updateUserPermissions = async (targetUserId, permissionsData) => {
    const userRef = doc(db, "users", targetUserId);
    try {
        await updateDoc(userRef, {
            permissions: permissionsData,
            permissionsLastUpdatedAt: serverTimestamp(),
        });
    } catch (error)
    {
        console.error(`Error updating permissions for user ${targetUserId}:`, error);
        throw error;
    }
};