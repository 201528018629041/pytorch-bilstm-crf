# encoding: utf-8
import re
import time

from data_utils import load_vocab_vectors, _load_words_tags_chars, _load_data, batch_generator
from model import create_crf_on_lstm_model
from utils import *

LEARNING_RATE = 0.001
WEIGHT_DECAY = 1e-4
SAVE_EVERY = 1

torch.manual_seed(1)


def train(word_vocab_size,
          tag_vocab_size,
          char_vocab_size,
          word_embeddings,
          train_data,
          valid_data,
          epochs=20):
    model = create_crf_on_lstm_model(word_vocab_size, tag_vocab_size, char_vocab_size, word_embeddings)
    optim = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
    # TODO: change naming to something better
    filename = re.sub("\.epoch[0-9]+$", "", '0')
    print(model)
    print("training model...")
    epoch = 0
    for ei in range(epoch + 1, epoch + epochs + 1):
        loss_sum = 0
        timer = time.time()
        batch_count = 0
        model.train()
        for word_x, char_x, y in batch_generator(*train_data):
            model.zero_grad()
            loss = torch.mean(model(word_x, char_x, y))  # forward pass and compute loss
            loss.backward()  # compute gradients
            optim.step()  # update parameters
            loss = scalar(loss)
            loss_sum += loss
            batch_count += 1
        timer = time.time() - timer
        loss_sum /= batch_count
        if ei % SAVE_EVERY and ei != epoch + epochs:
            save_checkpoint("", None, ei, loss_sum, timer)
        else:
            save_checkpoint(filename, model, ei, loss_sum, timer)

        loss_sum = 0
        batch_count = 0
        model.eval()
        with torch.no_grad():
            for word_x, char_x, y in batch_generator(*valid_data):
                loss_sum += scalar(torch.mean(model(word_x, char_x, y)))
                batch_count += 1

            print('validation loss: {}'.format(loss_sum / batch_count))


if __name__ == "__main__":
    words_file = "data/words.txt"
    tags_file = "data/tags.txt"
    chars_file = "data/chars.txt"
    valid_file = 'data/more_annotated_test.conll'
    train_file = 'data/more_annotated_train.conll'
    filtered_embeddings_file = "data/filtered_embeddings.txt"

    word2idx, tag2idx, char2idx = _load_words_tags_chars(words_file, tags_file, chars_file)
    train_data = _load_data(train_file, word2idx, tag2idx, char2idx)
    valid_data = _load_data(valid_file, word2idx, tag2idx, char2idx)
    train(
        len(word2idx),
        len(tag2idx),
        len(char2idx) + 1,
        load_vocab_vectors(filtered_embeddings_file),
        train_data,
        valid_data,
        epochs=100)
